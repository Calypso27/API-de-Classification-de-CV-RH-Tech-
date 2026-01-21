from django.contrib import admin
from .models import Category, Resume, Classification, JobPosting


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'keywords_preview')
    search_fields = ('name', 'keywords')
    ordering = ('name',)

    def keywords_preview(self, obj):
        """Affiche un aperçu des mots-clés (50 premiers caractères)"""
        if obj.keywords:
            return obj.keywords[:50] + '...' if len(obj.keywords) > 50 else obj.keywords
        return '-'
    keywords_preview.short_description = 'Mots-clés'


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'uploaded_at', 'has_text_content', 'classifications_count')
    list_filter = ('uploaded_at', 'user')
    search_fields = ('user__username', 'text_content')
    readonly_fields = ('uploaded_at', 'text_content')
    ordering = ('-uploaded_at',)

    def has_text_content(self, obj):
        """Indique si le texte a été extrait"""
        return bool(obj.text_content)
    has_text_content.boolean = True
    has_text_content.short_description = 'Texte extrait'

    def classifications_count(self, obj):
        """Nombre de classifications pour ce CV"""
        return obj.classifications.count()
    classifications_count.short_description = 'Classifications'


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'resume', 'category', 'confidence_score', 'classified_at')
    list_filter = ('category', 'classified_at')
    search_fields = ('resume__user__username', 'category__name')
    readonly_fields = ('classified_at',)
    ordering = ('-classified_at',)

    def get_queryset(self, request):
        """Optimise les requêtes avec select_related"""
        return super().get_queryset(request).select_related('resume', 'category', 'resume__user')


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'created_at')
    search_fields = ('title', 'description', 'category__name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_editable = ('is_active',)
