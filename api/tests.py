from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

from api.models import Message


class ScheduledMessagingAPITests(APITestCase):

    def setUp(self):
        self.future_time = timezone.now() + timedelta(hours=1)

        self.message = Message.objects.create(
            sender_name="Dennis",
            receiver_name="John",
            receiver_phone="+2348012345678",
            message="Hello John",
            scheduled_time=self.future_time
        )

    # ------------------------
    # Root endpoint
    # ------------------------
    def test_root_endpoint(self):
        url = reverse('root')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'active')
        self.assertIn('endpoints', response.data)

    # ------------------------
    # Create message
    # ------------------------
    def test_create_message_success(self):
        url = reverse('create-message')
        payload = {
            "sender_name": "Alice",
            "receiver_name": "Bob",
            "receiver_phone": "+12025550123",
            "message": "Scheduled greeting",
            "scheduled_time": (timezone.now() + timedelta(hours=2)).isoformat()
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['sender_name'], payload['sender_name'])
        self.assertTrue(
            Message.objects.filter(receiver_phone="+12025550123").exists()
        )

    def test_create_message_with_past_time_fails(self):
        url = reverse('create-message')
        payload = {
            "sender_name": "Alice",
            "receiver_name": "Bob",
            "receiver_phone": "+12025550123",
            "message": "Invalid schedule",
            "scheduled_time": (timezone.now() - timedelta(minutes=5)).isoformat()
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('scheduled_time', response.data)

    def test_create_message_invalid_phone_fails(self):
        url = reverse('create-message')
        payload = {
            "sender_name": "Alice",
            "receiver_name": "Bob",
            "receiver_phone": "08012345678",  # ❌ Not E.164
            "message": "Invalid phone",
            "scheduled_time": (timezone.now() + timedelta(hours=1)).isoformat()
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('receiver_phone', response.data)

    # ------------------------
    # List messages
    # ------------------------
    def test_list_messages(self):
        url = reverse('list-messages')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_messages_with_pagination(self):
        url = reverse('list-messages') + '?skip=0&limit=1'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # ------------------------
    # Get single message
    # ------------------------
    def test_get_message_success(self):
        url = reverse('get-message', args=[self.message.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.message.id)
        self.assertEqual(response.data['receiver_name'], "John")

    def test_get_message_not_found(self):
        url = reverse('get-message', args=[99999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)

    # ------------------------
    # Health check
    # ------------------------
    def test_health_check(self):
        url = reverse('health-check')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertEqual(response.data['service'], 'scheduled-messaging-api')
