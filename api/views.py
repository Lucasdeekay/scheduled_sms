from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Message
from .serializers import (
    MessageCreateSerializer,
    MessageResponseSerializer
)


class RootAPIView(APIView):
    def get(self, request):
        return Response({
            "message": "Scheduled Messaging API",
            "status": "active",
            "endpoints": {
                "create_message": "/messages/",
                "list_messages": "/messages/",
                "get_message": "/messages/{id}"
            }
        })

class CreateMessageAPIView(APIView):
    def post(self, request):
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        return Response(
            MessageResponseSerializer(message).data,
            status=status.HTTP_201_CREATED
        )

class ListMessagesAPIView(APIView):
    def get(self, request):
        skip = int(request.GET.get('skip', 0))
        limit = int(request.GET.get('limit', 100))

        queryset = Message.objects.all()[skip: skip + limit]

        return Response(
            MessageResponseSerializer(queryset, many=True).data
        )

class GetMessageAPIView(APIView):
    def get(self, request, message_id: int):
        try:
            message = Message.objects.get(pk=message_id)
        except Message.DoesNotExist:
            return Response(
                {"detail": f"Message with ID {message_id} not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            MessageResponseSerializer(message).data
        )

class HealthCheckAPIView(APIView):
    def get(self, request):
        return Response({
            "status": "healthy",
            "service": "scheduled-messaging-api"
        })
