from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
import logging

from . import serializers
from .models import Resume, Category, Classification, JobPosting
from .serializers import (
    ResumeSerializer, ResumeListSerializer,
    CategorySerializer, CategoryDetailSerializer,
    ClassificationSerializer, JobPostingSerializer
)
from .utils import extract_text, extract_skills as utils_extract_skills
from .ml_classifier import cv_classifier

logger = logging.getLogger(__name__)


class ResumeViewSet(viewsets.ModelViewSet):

    queryset = Resume.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ResumeListSerializer
        return ResumeSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Resume.objects.none()
        if self.request.user.is_staff:
            return Resume.objects.all()
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)

        try:
            # Extraire le texte du fichier
            logger.info(f"Extraction du texte pour le CV {resume.id}")
            text = extract_text(resume.file.path)
            resume.text_content = text
            resume.save()
            logger.info(f"Texte extrait avec succès pour le CV {resume.id}")

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
            resume.delete()
            raise serializers.ValidationError({
                'error': f"Impossible d'extraire le texte du fichier PDF/DOCX: {str(e)}"
            })

    @action(detail=True, methods=['post'], url_path='classify')
    def classify(self, request, pk=None):
        resume = self.get_object()

        if not resume.text_content:
            return Response(
                {'error': 'Aucun texte extrait du CV. Impossible de classifier.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if not cv_classifier.is_loaded:
                return Response(
                    {
                        'error': 'Modèle ML non disponible',
                        'message': 'Veuillez télécharger le modèle depuis Kaggle et exécuter train_model.py'
                    },
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            logger.info(f"Classification du CV {resume.id}")
            predicted_category, confidence = cv_classifier.predict(resume.text_content)

            category, created = Category.objects.get_or_create(
                name=predicted_category,
                defaults={'keywords': ''}
            )

            if created:
                logger.info(f"Nouvelle catégorie créée: {predicted_category}")

            resume.classifications.all().delete()

            classification = Classification.objects.create(
                resume=resume,
                category=category,
                confidence_score=confidence
            )

            logger.info(f"CV {resume.id} classifié comme {predicted_category} ({confidence:.2%})")

            serializer = ClassificationSerializer(classification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erreur lors de la classification: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la classification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='by-category')
    def by_category(self, request):
        category_name = request.query_params.get('category')

        if not category_name:
            return Response(
                {'error': 'Paramètre "category" requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            classifications = Classification.objects.filter(
                category__name__iexact=category_name
            ).select_related('resume', 'category', 'resume__user')

            if not classifications.exists():
                return Response(
                    {
                        'message': f'Aucun CV trouvé dans la catégorie "{category_name}"',
                        'category': category_name,
                        'count': 0,
                        'results': []
                    },
                    status=status.HTTP_200_OK
                )

            data = [{
                'classification_id': c.id,
                'resume_id': c.resume.id,
                'user': c.resume.user.username,
                'category': c.category.name,
                'confidence': round(c.confidence_score, 4),
                'confidence_percent': f"{c.confidence_score * 100:.2f}%",
                'uploaded_at': c.resume.uploaded_at,
                'classified_at': c.classified_at
            } for c in classifications]

            return Response({
                'category': category_name,
                'count': len(data),
                'results': data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche par catégorie: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la recherche: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'], url_path='extract-skills')
    def get_resume_skills(self, request, pk=None):
        resume = self.get_object()

        if not resume.text_content:
            return Response(
                {'error': 'Aucun texte extrait du CV. Impossible d\'extraire les compétences.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            logger.info(f"Extraction des compétences du CV {resume.id}")

            # Extraire les compétences
            skills = utils_extract_skills(resume.text_content)

            return Response({
                'resume_id': resume.id,
                'user': resume.user.username,
                'skills_found': len(skills),
                'skills': sorted(skills),
                'extracted_at': resume.uploaded_at
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des compétences: {str(e)}")
            return Response(
                {'error': f'Erreur lors de l\'extraction des compétences: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategorySerializer

    @action(detail=True, methods=['get'], url_path='resumes')
    def get_category_resumes(self, request, pk=None):
        category = self.get_object()
        classifications = category.classification_set.select_related('resume', 'resume__user')

        data = [{
            'resume_id': c.resume.id,
            'user': c.resume.user.username,
            'confidence': round(c.confidence_score, 4),
            'uploaded_at': c.resume.uploaded_at,
            'classified_at': c.classified_at
        } for c in classifications]

        return Response({
            'category': category.name,
            'count': len(data),
            'resumes': data
        })


class ClassificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Classification.objects.all().select_related('resume', 'category')
    serializer_class = ClassificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Classification.objects.none()
        if self.request.user.is_staff:
            return Classification.objects.all()
        return Classification.objects.filter(resume__user=self.request.user)

    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        classifications = self.get_queryset()

        stats = {
            'total_classifications': classifications.count(),
            'average_confidence': round(
                classifications.aggregate(
                    avg=Avg('confidence_score')
                )['avg'] or 0, 4
            ),
            'categories_distribution': {}
        }

        # Distribution par catégorie
        for category in Category.objects.all():
            count = classifications.filter(category=category).count()
            if count > 0:
                stats['categories_distribution'][category.name] = count

        return Response(stats)


class JobPostingViewSet(viewsets.ModelViewSet):
    queryset = JobPosting.objects.all()
    serializer_class = JobPostingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.query_params.get('active') == 'true':
            return JobPosting.objects.filter(is_active=True)
        if not self.request.user.is_staff:
            return JobPosting.objects.filter(is_active=True)
        return JobPosting.objects.all()
