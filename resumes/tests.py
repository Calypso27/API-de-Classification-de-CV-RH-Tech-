from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
import tempfile
import os

from .models import Resume, Category, Classification, JobPosting
from .serializers import ResumeSerializer, CategorySerializer, ClassificationSerializer


class CategoryModelTest(TestCase):
    """Tests pour le modèle Category"""

    def setUp(self):
        self.category = Category.objects.create(
            name="Python Developer",
            keywords="python, django, flask, fastapi"
        )

    def test_category_creation(self):
        """Test de création d'une catégorie"""
        self.assertEqual(self.category.name, "Python Developer")
        self.assertIn("python", self.category.keywords)

    def test_category_str(self):
        """Test de la représentation string"""
        self.assertEqual(str(self.category), "Python Developer")

    def test_category_unique_name(self):
        """Test que le nom de catégorie est unique"""
        with self.assertRaises(Exception):
            Category.objects.create(name="Python Developer", keywords="test")


class ResumeModelTest(TestCase):
    """Tests pour le modèle Resume"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_resume_creation(self):
        """Test de création d'un CV"""
        resume = Resume.objects.create(
            user=self.user,
            text_content="Python developer with 5 years experience"
        )
        self.assertEqual(resume.user.username, 'testuser')
        self.assertIsNotNone(resume.uploaded_at)

    def test_resume_str(self):
        """Test de la représentation string"""
        resume = Resume.objects.create(
            user=self.user,
            text_content="Test content"
        )
        self.assertIn('testuser', str(resume))


class ClassificationModelTest(TestCase):
    """Tests pour le modèle Classification"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name="Data Science",
            keywords="python, machine learning, data"
        )
        self.resume = Resume.objects.create(
            user=self.user,
            text_content="Data scientist with ML experience"
        )

    def test_classification_creation(self):
        """Test de création d'une classification"""
        classification = Classification.objects.create(
            resume=self.resume,
            category=self.category,
            confidence_score=0.85
        )
        self.assertEqual(classification.confidence_score, 0.85)
        self.assertEqual(classification.category.name, "Data Science")

    def test_classification_str(self):
        """Test de la représentation string"""
        classification = Classification.objects.create(
            resume=self.resume,
            category=self.category,
            confidence_score=0.92
        )
        self.assertIn("Data Science", str(classification))


class JobPostingModelTest(TestCase):
    """Tests pour le modèle JobPosting"""

    def setUp(self):
        self.category = Category.objects.create(
            name="Web Development",
            keywords="html, css, javascript"
        )

    def test_jobposting_creation(self):
        """Test de création d'une offre d'emploi"""
        job = JobPosting.objects.create(
            title="Senior Web Developer",
            description="Looking for experienced web developer",
            category=self.category,
            is_active=True
        )
        self.assertEqual(job.title, "Senior Web Developer")
        self.assertTrue(job.is_active)

    def test_jobposting_str(self):
        """Test de la représentation string"""
        job = JobPosting.objects.create(
            title="Junior Developer",
            description="Entry level position",
            category=self.category
        )
        self.assertEqual(str(job), "Junior Developer")


class AuthenticationAPITest(APITestCase):
    """Tests pour l'authentification JWT"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()

    def test_obtain_token(self):
        """Test d'obtention du token JWT"""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_invalid_credentials(self):
        """Test avec identifiants invalides"""
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Test de rafraîchissement du token"""
        # Obtenir les tokens
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = response.data['refresh']

        # Rafraîchir le token
        response = self.client.post('/api/token/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class CategoryAPITest(APITestCase):
    """Tests pour l'API des catégories"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name="Java Developer",
            keywords="java, spring, hibernate"
        )

    def test_list_categories(self):
        """Test de listage des catégories"""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_category(self):
        """Test de création d'une catégorie"""
        response = self.client.post('/api/categories/', {
            'name': 'DevOps Engineer',
            'keywords': 'docker, kubernetes, ci/cd'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'DevOps Engineer')

    def test_retrieve_category(self):
        """Test de récupération d'une catégorie"""
        response = self.client.get(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Java Developer')

    def test_update_category(self):
        """Test de mise à jour d'une catégorie"""
        response = self.client.patch(f'/api/categories/{self.category.id}/', {
            'keywords': 'java, spring, hibernate, microservices'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('microservices', response.data['keywords'])

    def test_delete_category(self):
        """Test de suppression d'une catégorie"""
        response = self.client.delete(f'/api/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_access(self):
        """Test d'accès non authentifié"""
        self.client.logout()
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ResumeAPITest(APITestCase):
    """Tests pour l'API des CV"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.resume = Resume.objects.create(
            user=self.user,
            text_content="Experienced Python developer"
        )

    def test_list_resumes(self):
        """Test de listage des CV"""
        response = self.client.get('/api/resumes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_sees_only_own_resumes(self):
        """Test que l'utilisateur ne voit que ses propres CV"""
        # Créer un CV pour un autre utilisateur
        Resume.objects.create(
            user=self.other_user,
            text_content="Other user resume"
        )

        response = self.client.get('/api/resumes/')
        # L'utilisateur ne doit voir que son CV
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_resume(self):
        """Test de récupération d'un CV"""
        response = self.client.get(f'/api/resumes/{self.resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_resume(self):
        """Test de suppression d'un CV"""
        response = self.client.delete(f'/api/resumes/{self.resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ResumeClassifyAPITest(APITestCase):
    """Tests pour la classification des CV"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.resume = Resume.objects.create(
            user=self.user,
            text_content="Python developer with Django and Flask experience"
        )

        self.resume_no_text = Resume.objects.create(
            user=self.user,
            text_content=""
        )

    @patch('resumes.views.cv_classifier')
    def test_classify_resume_success(self, mock_classifier):
        """Test de classification réussie"""
        mock_classifier.is_loaded = True
        mock_classifier.predict.return_value = ("Python Developer", 0.92)

        response = self.client.post(f'/api/resumes/{self.resume.id}/classify/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['category_name'], "Python Developer")
        self.assertAlmostEqual(response.data['confidence_score'], 0.92, places=2)

    def test_classify_resume_no_text(self):
        """Test de classification sans texte extrait"""
        response = self.client.post(f'/api/resumes/{self.resume_no_text.id}/classify/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('resumes.views.cv_classifier')
    def test_classify_resume_model_not_loaded(self, mock_classifier):
        """Test de classification avec modèle non chargé"""
        mock_classifier.is_loaded = False

        response = self.client.post(f'/api/resumes/{self.resume.id}/classify/')
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)


class ResumeByCategoryAPITest(APITestCase):
    """Tests pour la recherche par catégorie"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name="Data Science",
            keywords="python, ml, data"
        )
        self.resume = Resume.objects.create(
            user=self.user,
            text_content="Data scientist resume"
        )
        Classification.objects.create(
            resume=self.resume,
            category=self.category,
            confidence_score=0.88
        )

    def test_by_category_success(self):
        """Test de recherche par catégorie"""
        response = self.client.get('/api/resumes/by-category/', {'category': 'Data Science'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_by_category_not_found(self):
        """Test de recherche catégorie inexistante"""
        response = self.client.get('/api/resumes/by-category/', {'category': 'Unknown'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_by_category_missing_param(self):
        """Test de recherche sans paramètre"""
        response = self.client.get('/api/resumes/by-category/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResumeExtractSkillsAPITest(APITestCase):
    """Tests pour l'extraction de compétences"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.resume = Resume.objects.create(
            user=self.user,
            text_content="Expert in Python, Django, and PostgreSQL with Docker experience"
        )

    def test_extract_skills_success(self):
        """Test d'extraction de compétences"""
        response = self.client.get(f'/api/resumes/{self.resume.id}/extract-skills/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('skills', response.data)
        self.assertIn('skills_found', response.data)


class ClassificationAPITest(APITestCase):
    """Tests pour l'API des classifications"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name="Frontend Developer",
            keywords="javascript, react, vue"
        )
        self.resume = Resume.objects.create(
            user=self.user,
            text_content="Frontend developer resume"
        )
        self.classification = Classification.objects.create(
            resume=self.resume,
            category=self.category,
            confidence_score=0.78
        )

    def test_list_classifications(self):
        """Test de listage des classifications"""
        response = self.client.get('/api/classifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_classification(self):
        """Test de récupération d'une classification"""
        response = self.client.get(f'/api/classifications/{self.classification.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stats_endpoint(self):
        """Test de l'endpoint des statistiques"""
        response = self.client.get('/api/classifications/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_classifications', response.data)
        self.assertIn('average_confidence', response.data)
        self.assertIn('categories_distribution', response.data)


class JobPostingAPITest(APITestCase):
    """Tests pour l'API des offres d'emploi"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
            is_staff=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = Category.objects.create(
            name="Backend Developer",
            keywords="python, java, nodejs"
        )
        self.job = JobPosting.objects.create(
            title="Senior Backend Developer",
            description="Looking for experienced backend developer",
            category=self.category,
            is_active=True
        )
        self.inactive_job = JobPosting.objects.create(
            title="Closed Position",
            description="This position is closed",
            category=self.category,
            is_active=False
        )

    def test_list_jobpostings_user(self):
        """Test que l'utilisateur ne voit que les offres actives"""
        response = self.client.get('/api/jobpostings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # L'utilisateur normal ne voit que les offres actives
        for job in response.data['results']:
            self.assertTrue(job['is_active'])

    def test_list_jobpostings_staff(self):
        """Test que le staff voit toutes les offres"""
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get('/api/jobpostings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_jobposting(self):
        """Test de création d'une offre"""
        response = self.client.post('/api/jobpostings/', {
            'title': 'New Position',
            'description': 'New job description',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SerializerValidationTest(TestCase):
    """Tests de validation des serializers"""

    def test_resume_file_extension_validation(self):
        """Test de validation de l'extension du fichier"""
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"file content",
            content_type="text/plain"
        )
        serializer = ResumeSerializer(data={'file': invalid_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)

    def test_resume_file_size_validation(self):
        """Test de validation de la taille du fichier"""
        # Créer un fichier de plus de 5MB
        large_content = b"x" * (6 * 1024 * 1024)  # 6MB
        large_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        serializer = ResumeSerializer(data={'file': large_file})
        self.assertFalse(serializer.is_valid())
        self.assertIn('file', serializer.errors)

    def test_classification_confidence_validation(self):
        """Test de validation du score de confiance"""
        user = User.objects.create_user(username='test', password='test')
        category = Category.objects.create(name="Test", keywords="test")
        resume = Resume.objects.create(user=user, text_content="test")

        # Score invalide (> 1)
        serializer = ClassificationSerializer(data={
            'resume': resume.id,
            'category': category.id,
            'confidence_score': 1.5
        })
        self.assertFalse(serializer.is_valid())

        # Score invalide (< 0)
        serializer = ClassificationSerializer(data={
            'resume': resume.id,
            'category': category.id,
            'confidence_score': -0.5
        })
        self.assertFalse(serializer.is_valid())
