from django.urls import path
from .views import (
    DocumentUploadView,
    DocumentRetrieveView,
    DocumentImproveView,
    DocumentExportView,
    DocumentStatusView,
    DocumentVersionRetrieveView
)

urlpatterns = [
    # Document upload and processing
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    
    # Document retrieval and management
    path('documents/<uuid:id>/', DocumentRetrieveView.as_view(), name='document-retrieve'),
    path('documents/<uuid:id>/improve/', DocumentImproveView.as_view(), name='document-improve'),
    path('documents/<uuid:id>/export/', DocumentExportView.as_view(), name='document-export'),
    path('documents/<uuid:id>/status/', DocumentStatusView.as_view(), name='document-status'),
    
    # Version-specific endpoints
    path('documents/<uuid:id>/versions/<uuid:version_id>/', 
         DocumentVersionRetrieveView.as_view(), 
         name='document-version-retrieve'),
]