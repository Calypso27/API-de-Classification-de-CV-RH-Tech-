from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    keywords = models.TextField(help_text="Mots-clés séparés par virgules")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    text_content = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"CV de {self.user.username} - {self.uploaded_at}"


class Classification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='classifications')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    confidence_score = models.FloatField()
    classified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-classified_at']

    def __str__(self):
        return f"{self.resume} -> {self.category.name} ({self.confidence_score:.2f})"


class JobPosting(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
