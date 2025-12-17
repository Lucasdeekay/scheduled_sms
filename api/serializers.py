from rest_framework import serializers
from .models import Message
from django.utils import timezone
class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender_name', 'receiver_name', 'receiver_phone',
        'message', 'scheduled_time']
    
    def validate_scheduled_time(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Must be a future time.")
        return value
    
class MessageResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender_name', 'receiver_name', 'receiver_phone',
        'message', 'scheduled_time', 'sent_at', 'created_at']