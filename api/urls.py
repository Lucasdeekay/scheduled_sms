from django.urls import path
from . import views
urlpatterns = [
    path('', views.root),
    path('messages/', views.create_message, name='create_message'),
    path('messages/', views.list_messages,  name='list_messages'),
    path('messages/int:message_id/', views.get_message, name='get_message'),
    path('health/', views.health_check, name='health'),
]