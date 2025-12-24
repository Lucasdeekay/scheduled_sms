from django.urls import path
from .views import send_due_messages

urlpatterns = [
    path('trigger', send_due_messages, name='send_sms'),
]
