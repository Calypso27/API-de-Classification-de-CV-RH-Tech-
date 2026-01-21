from rest_framework import serializers
from .models import Resume, Category, Classification, JobPosting


class CategorySerializer(serializers.ModelSerializer):
    resume_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'keywords', 'created_at', 'resume_count']

    def get_resume_count(self, obj):
        return obj.classification_set.count()


class ResumeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    classifications = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['id', 'file', 'text_content', 'uploaded_at', 'user_name', 'classifications']
        read_only_fields = ['id', 'text_content', 'uploaded_at', 'user_name', 'classifications']

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

    def get_classifications(self, obj):
        classifications = obj.classifications.all()
        return ClassificationSerializer(classifications, many=True).data


class ClassificationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    resume_id = serializers.IntegerField(source='resume.id', read_only=True)
    user_name = serializers.CharField(source='resume.user.username', read_only=True)
    resume_file = serializers.CharField(source='resume.file.name', read_only=True)

    class Meta:
        model = Classification
        fields = [
            'id', 'resume_id', 'user_name', 'resume_file',
            'category', 'category_name', 'confidence_score', 'classified_at'
        ]
        read_only_fields = ['id', 'classified_at', 'resume_id', 'user_name', 'resume_file']

    def validate_confidence_score(self, value):
        if not (0 <= value <= 1):
            raise serializers.ValidationError(
                "Le score de confiance doit être entre 0 et 1."
            )
        return value


class JobPostingSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at']


# Serializers optionnels pour les listes

class ResumeListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    classification_count = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['id', 'uploaded_at', 'user_name', 'classification_count']
        read_only_fields = ['id', 'uploaded_at', 'user_name']

    def get_classification_count(self, obj):
        return obj.classifications.count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    resumes = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'keywords', 'created_at', 'resumes']

    def get_resumes(self, obj):
        classifications = obj.classification_set.select_related('resume')
        return ClassificationSerializer(classifications, many=True).data
