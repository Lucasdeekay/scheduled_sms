from django.urls import path
from .views import (
    RootAPIView,
    CreateMessageAPIView,
    ListMessagesAPIView,
    GetMessageAPIView,
    HealthCheckAPIView
)

urlpatterns = [
    path('', RootAPIView.as_view(), name='root'),
    path('messages/', CreateMessageAPIView.as_view(), name='create-message'),
    path('messages/list/', ListMessagesAPIView.as_view(), name='list-messages'),
    path('messages/<int:message_id>/', GetMessageAPIView.as_view(), name='get-message'),
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
]
