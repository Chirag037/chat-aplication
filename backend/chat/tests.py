from django.test import TestCase
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from .models import Room, Message

class SimpleChatTest(APITestCase):
    
    def setUp(self):
        """Setup fake data for tests"""
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_room_name(self):
        """Check if room name is saved correctly"""
        room = Room.objects.create(name="Public Lounge")
        self.assertEqual(room.name, "Public Lounge")

    def test_message_user(self):
        """Check if message remembers who sent it"""
        room = Room.objects.create(name="Test Room")
        msg = Message.objects.create(user=self.user, room=room, content="Hi!")
        self.assertEqual(msg.user.username, "tester")

    def test_api_connection(self):
        url = '/api/health/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_is_json(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/ai/proxy/'
        response = self.client.get(url)
        # Verify the header specifically says application/json
        self.assertIn('application/json', response['Content-Type'])

    def test_api_respond_json_with_different_accept_type(self):
        """Test that the API still responds with JSON even if a different Accept header is sent"""
        self.client.force_authenticate(user=self.user)
        url = '/api/ai/proxy/'
        response = self.client.get(url, HTTP_ACCEPT='text/html')
        self.assertIn('application/json', response['Content-Type'])

    def test_api_send_html_content_type(self):      
        self.client.force_authenticate(user=self.user)
        url = '/api/ai/proxy/'
        data = "<html><body>Hello</body></html>"
        response = self.client.post(url, data=data, content_type='text/html')
        self.assertEqual(response.status_code, 415)