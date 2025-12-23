from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    # Columns to display in the list view
    list_display = (
        'receiver_name', 
        'receiver_phone', 
        'sender_name', 
        'scheduled_time', 
        'is_sent',  # Custom method defined below
        'created_at'
    )
    
    # Filters on the right sidebar
    list_filter = ('scheduled_time', 'created_at', 'sent_at')
    
    # Search box functionality
    search_fields = ('sender_name', 'receiver_name', 'receiver_phone', 'message')
    
    # Organize the detail view into sections
    fieldsets = (
        ('Contact Info', {
            'fields': ('sender_name', 'receiver_name', 'receiver_phone')
        }),
        ('Content', {
            'fields': ('message',)
        }),
        ('Scheduling', {
            'fields': ('scheduled_time', 'sent_at')
        }),
    )
    
    # Make sent_at and created_at read-only to prevent accidental edits
    readonly_fields = ('created_at', 'sent_at')

    # Add a visual indicator for "Sent" status
    @admin.display(boolean=True, description='Status: Sent')
    def is_sent(self, obj):
        return obj.sent_at is not None