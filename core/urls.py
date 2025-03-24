from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.DocumentViewSet, basename='document')
router.register(r'suggestions', views.SuggestionViewSet, basename='suggestion')
router.register(r'templates', views.TemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
