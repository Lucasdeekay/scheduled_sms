from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from .models import Message
from .serializers import MessageCreateSerializer, MessageResponseSerializer


@api_view(['GET'])
def root(request):
    return Response({
    "message": "Scheduled Messaging API",
    "status": "active",
    "endpoints": {
    "create_message": "/messages/",
    "list_messages": "/messages/",
    "get_message": "/messages/{id}"
    }
    })

@api_view(['POST'])
def create_message(request):
    ser = MessageCreateSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    msg = ser.save()
    return Response(MessageResponseSerializer(msg).data,
status=status.HTTP_201_CREATED)

@api_view(['GET'])
def list_messages(request):
    skip  = int(request.GET.get('skip', 0))
    limit = int(request.GET.get('limit', 100))
    qs    = Message.objects.all()[skip:skip+limit]
    return Response(MessageResponseSerializer(qs, many=True).data)


@api_view(['GET'])
def get_message(request, message_id: int):
    try:
        msg = Message.objects.get(pk=message_id)
    except Message.DoesNotExist:
        return Response({"detail": f"Message with ID {message_id} not found"},
        status=status.HTTP_404_NOT_FOUND)
    return Response(MessageResponseSerializer(msg).data)

@api_view(['GET'])
def health_check(request):
    return Response({"status": "healthy", "service": "scheduled-messaging-api"})