from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet

# Create a router and register the viewset
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

# Define URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
