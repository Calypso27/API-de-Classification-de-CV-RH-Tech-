from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeViewSet, CategoryViewSet, ClassificationViewSet, JobPostingViewSet

router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'classifications', ClassificationViewSet, basename='classification')
router.register(r'jobpostings', JobPostingViewSet, basename='jobposting')

urlpatterns = [
    path('', include(router.urls)),
]
