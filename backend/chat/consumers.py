import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Room

class ChatConsumer(AsyncWebsocketConsumer):
    async def confirm_user(self):
        # We'll rely on the frontend sending the access token or having been authenticated via session
        # For now, we'll implement a simple join where the frontend passes the username/id
        pass

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')
        username = data.get('username')

        if not message_content or not username:
            return

        # Save message to database
        saved_msg = await self.save_message(username, self.room_id, message_content)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'username': username,
                'created_at': saved_msg['created_at']
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'content': event['message'],
            'username': event['username'],
            'created_at': event['created_at'],
            'room': self.room_id
        }))

    @database_sync_to_async
    def save_message(self, username, room_id, content):
        user = User.objects.get(username=username)
        room = Room.objects.get(id=room_id)
        msg = Message.objects.create(user=user, room=room, content=content)
        return {
            'id': msg.id,
            'created_at': msg.created_at.isoformat()
        }
