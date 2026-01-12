from rest_framework import serializers
from .models import Resume, Category, Classification, JobPosting
from .utils import extract_text, extract_skills


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'keywords', 'created_at']


class ResumeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Resume
        fields = ['id', 'file', 'text_content', 'uploaded_at', 'user_name']
        read_only_fields = ['text_content', 'uploaded_at', 'user_name']

    def validate_file(self, value):
        # Vérifier l'extension
        if not value.name.endswith(('.pdf', '.docx')):
            raise serializers.ValidationError(
                "Format non supporté. Utilisez PDF ou DOCX."
            )

        # Vérifier la taille (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "Fichier trop volumineux. Maximum 5MB."
            )

        return value


class ClassificationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    resume_id = serializers.IntegerField(source='resume.id', read_only=True)

    class Meta:
        model = Classification
        fields = ['id', 'resume_id', 'category', 'category_name',
                  'confidence_score', 'classified_at']
        read_only_fields = ['classified_at']


class JobPostingSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = JobPosting
        fields = ['id', 'title', 'description', 'category',
                  'category_name', 'created_at', 'is_active']