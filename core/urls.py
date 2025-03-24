from django.urls import path
from .views import upload_document, get_document_view

urlpatterns = [
    path('upload/', upload_document, name='upload_document'),
    path('documents/<uuid:id>/', get_document_view, name='get_document'),
]
