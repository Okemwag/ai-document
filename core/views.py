from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .services.document_processor import create_document, get_document
# from .tasks import improve_document

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """
    Handle document upload.
    """
    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    try:
        document = create_document(request.user, file)
        # improve_document.delay(document.id)  # Commented out task function
        return JsonResponse({'message': 'File uploaded successfully', 'document_id': document.id})
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_view(request, id):
    """
    Get original and improved document.
    """
    document = get_document(request.user, id)
    if document:
        return JsonResponse({
            'title': document.title,
            'original_content': document.original_content,
            'improved_content': document.improved_content,
            'status': document.status
        })
    return JsonResponse({'error': 'Document not found'}, status=404)
