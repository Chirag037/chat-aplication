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
        action = data.get('action', 'send')
        username = data.get('username')

        if not username: return

        if action == 'send':
            message_content = data.get('message')
            if not message_content: return
            saved_msg = await self.save_message(username, self.room_id, message_content)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'username': username,
                    'created_at': saved_msg['created_at'],
                    'id': saved_msg['id']
                }
            )
        
        elif action == 'delete':
            msg_id = data.get('message_id')
            if await self.delete_message(username, msg_id):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_deleted',
                        'message_id': msg_id
                    }
                )

        elif action == 'edit':
            msg_id = data.get('message_id')
            new_content = data.get('message')
            if await self.edit_message(username, msg_id, new_content):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_edited',
                        'message_id': msg_id,
                        'message': new_content
                    }
                )

    # Handlers for Group Events
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'content': event['message'],
            'username': event['username'],
            'created_at': event['created_at'],
            'id': event['id'],
            'room': self.room_id
        }))

    async def message_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'message_id': event['message_id'],
            'room': self.room_id
        }))

    async def message_edited(self, event):
        await self.send(text_data=json.dumps({
            'type': 'edit',
            'message_id': event['message_id'],
            'content': event['message'],
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

    @database_sync_to_async
    def delete_message(self, username, msg_id):
        try:
            msg = Message.objects.get(id=msg_id, user__username=username)
            msg.delete()
            return True
        except Message.DoesNotExist:
            return False

    @database_sync_to_async
    def edit_message(self, username, msg_id, content):
        try:
            msg = Message.objects.get(id=msg_id, user__username=username)
            msg.content = content
            msg.save()
            return True
        except Message.DoesNotExist:
            return False
