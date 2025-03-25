from django.contrib import admin
from .models import DocumentVersion

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'uploaded_at', 'processed_at')
    list_filter = ('status', 'uploaded_at', 'processed_at')
    search_fields = ('user__username', 'original_file', 'improved_file')
    readonly_fields = ('uploaded_at', 'processed_at')

    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Original Document', {
            'fields': ('original_file', 'original_text')
        }),
        ('Improved Document', {
            'fields': ('improved_file', 'improved_text')
        }),
        ('Suggestions', {
            'fields': ('grammar_suggestions', 'style_suggestions', 'clarity_suggestions')
        }),
        ('Status and Tracking', {
            'fields': ('status', 'uploaded_at', 'processed_at')
        }),
    )

    def has_add_permission(self, request):
        # Prevent creating new DocumentVersion objects via the admin interface
        return False

    def has_change_permission(self, request, obj=None):
        # Allow changing existing objects
        return True

    def has_delete_permission(self, request, obj=None):
        # Allow deletion of existing objects
        return True

