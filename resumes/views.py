from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import os

from . import serializers
from .models import Resume, Category, Classification, JobPosting
from .serializers import (
    ResumeSerializer, CategorySerializer,
    ClassificationSerializer, JobPostingSerializer
)
from .utils import extract_text, extract_skills as utils_extract_skills


class ResumeViewSet(viewsets.ModelViewSet):

    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)

        try:
            # Extraire le texte du fichier
            text = extract_text(resume.file.path)
            resume.text_content = text
            resume.save()
        except Exception as e:
            # Si l'extraction échoue, supprimer le CV
            resume.delete()
            raise serializers.ValidationError({
                'error': f"Impossible d'extraire le texte: {str(e)}"
            })

    @action(detail=True, methods=['post'], url_path='classify')
    def classify(self, request, pk=None, cv_classifier=None):
        resume = self.get_object()

        # Vérifier que le texte a été extrait
        if not resume.text_content:
            return Response(
                {'error': 'Aucun texte extrait du CV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Utiliser le modèle pré-entraîné
            predicted_category, confidence = cv_classifier.predict(resume.text_content)

            # Créer ou récupérer la catégorie
            category, _ = Category.objects.get_or_create(
                name=predicted_category,
                defaults={'keywords': ''}
            )

            # Sauvegarder la classification
            classification = Classification.objects.create(
                resume=resume,
                category=category,
                confidence_score=confidence
            )

            serializer = ClassificationSerializer(classification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
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

        classifications = Classification.objects.filter(
            category__name__iexact=category_name
        ).select_related('resume', 'category', 'resume__user')

        if not classifications.exists():
            return Response(
                {'message': f'Aucun CV dans la catégorie "{category_name}"'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = [{
            'resume_id': c.resume.id,
            'user': c.resume.user.username,
            'category': c.category.name,
            'confidence': round(c.confidence_score, 2),
            'uploaded_at': c.resume.uploaded_at,
            'classified_at': c.classified_at
        } for c in classifications]

        return Response({
            'category': category_name,
            'count': len(data),
            'results': data
        })

    @action(detail=True, methods=['get'], url_path='extract-skills')
    def get_resume_skills(self, request, pk=None):
        resume = self.get_object()

        if not resume.text_content:
            return Response(
                {'error': 'Aucun texte extrait du CV'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Extraire les compétences
        skills = utils_extract_skills(resume.text_content)

        return Response({
            'resume_id': resume.id,
            'skills_found': len(skills),
            'skills': sorted(skills)
        })
