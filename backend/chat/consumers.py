import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Room, MessageRead

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        await self.accept()
        
    async def disconnect(self, close_code):
        if hasattr(self, 'notification_group'):
            await self.channel_layer.group_discard(
                self.notification_group,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        username = data.get('username')

        if action == 'join' and username:
            self.username = username
            self.notification_group = f'notify_{username}'
            await self.channel_layer.group_add(
                self.notification_group,
                self.channel_name
            )
            # Mark all pending messages for this user as delivered across ALL rooms
            room_ids = await self.mark_all_as_delivered(username)
            for rid in room_ids:
                await self.channel_layer.group_send(
                    f'chat_{rid}',
                    {
                        'type': 'status_update',
                        'status': 'delivered',
                        'username': username,
                        'room_id': rid
                    }
                )
            return

        # For any non-join messages, require that the socket has identified itself.
        if not getattr(self, 'username', None):
            return
            
    async def notify_delivery_check(self, event):
        """Called when someone sends a message to a room this user is in."""
        msg_id = event['message_id']
        room_id = event['room_id']
        sender_username = event['sender_username']
        
        # Mark this specific message as delivered
        await self.mark_msg_delivered(msg_id)
        
        # Notify the room group that it's now delivered
        await self.channel_layer.group_send(
            f'chat_{room_id}',
            {
                'type': 'status_update',
                'status': 'delivered',
                'username': self.username,
                'room_id': room_id
            }
        )

    @database_sync_to_async
    def mark_msg_delivered(self, msg_id):
        Message.objects.filter(id=msg_id).update(status='delivered')

    @database_sync_to_async
    def mark_all_as_delivered(self, username):
        # Find all sent messages addressed to rooms this user is in (sent by others)
        user_rooms = Room.objects.filter(participants__username=username)
        msgs_to_update = Message.objects.filter(room__in=user_rooms, status='sent').exclude(user__username=username)
        # Get distinct room IDs that will be affected
        affected_room_ids = list(msgs_to_update.values_list('room_id', flat=True).distinct())
        # Bulk update
        msgs_to_update.update(status='delivered')
        return affected_room_ids

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

        # Since JWT isn't in WS headers, we rely on the 'join' action to identify the user
        pass

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

        if action == 'join':
            # Identify current socket connection and trigger delivery marks for pending messages
            if not username:
                return
            self.username = username
            await self.mark_messages_delivered(username, self.room_id)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'status_update',
                    'status': 'delivered',
                    'username': username,
                    'room_id': self.room_id
                }
            )
            return

        # After join, ignore client-provided username and use the bound identity.
        if not getattr(self, 'username', None):
            return
        username = self.username

        if action == 'send':
            message_content = data.get('message')
            if not message_content: return
            saved_msg = await self.save_message(username, self.room_id, message_content)
            
            # Broadcast message to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'username': username,
                    'created_at': saved_msg['created_at'],
                    'id': saved_msg['id'],
                    'room_type': saved_msg['room_type'],
                }
            )

            # PING other participants' notification groups to trigger "Delivered" status
            other_participants = await self.get_other_participants(username, self.room_id)
            for participant_username in other_participants:
                await self.channel_layer.group_send(
                    f'notify_{participant_username}',
                    {
                        'type': 'notify_delivery_check',
                        'message_id': saved_msg['id'],
                        'room_id': self.room_id,
                        'sender_username': username
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
        
        elif action == 'mark_read':
            room_type = await self.get_room_type(self.room_id)
            if room_type == 'direct':
                did_mark = await self.mark_messages_viewed_if_direct(username, self.room_id)
                if did_mark:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'status_update',
                            'room_id': self.room_id,
                            'status': 'viewed',
                            'username': username
                        }
                    )
            elif room_type == 'group':
                # Bulk-create MessageRead entries for all unseen messages
                results = await self.mark_all_group_messages_seen(username, self.room_id)
                for result in results:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'read_receipt',
                            'message_id': result['message_id'],
                            'seen_by': result['seen_by'],
                        }
                    )

        elif action == 'mark_message_seen':
            msg_id = data.get('message_id')
            if not msg_id:
                return
            result = await self.record_message_seen(username, self.room_id, msg_id)
            if result:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_receipt',
                        'message_id': result['message_id'],
                        'seen_by': result['seen_by'],
                    }
                )

    # Handlers for Group Events
    async def chat_message(self, event):
        # When a message is broadcast, the recipient's consumer marks it as delivered
        username = getattr(self, 'username', None)
        if username and username != event['username']:
            await self.mark_messages_delivered(username, self.room_id)
            # Notify the sender that it was delivered
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'status_update',
                    'status': 'delivered',
                    'username': username,
                    'room_id': self.room_id
                }
            )

        await self.send(text_data=json.dumps({
            'type': 'message',
            'content': event['message'],
            'username': event['username'],
            'created_at': event['created_at'],
            'id': event['id'],
            'status': event.get('status', 'sent'),
            'room': self.room_id,
            'room_type': event.get('room_type'),
        }))

    async def status_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'status': event['status'],
            'username': event['username'],
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

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'message_id': event['message_id'],
            'seen_by': event['seen_by'],
            'room': self.room_id
        }))

    @database_sync_to_async
    def save_message(self, username, room_id, content):
        user = User.objects.get(username=username)
        room = Room.objects.get(id=room_id)
        msg = Message.objects.create(user=user, room=room, content=content)
        return {
            'id': msg.id,
            'created_at': msg.created_at.isoformat(),
            'room_type': room.type,
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

    @database_sync_to_async
    def mark_messages_delivered(self, username, room_id):
        # All messages NOT by this user in this room become delivered
        Message.objects.filter(room_id=room_id, status='sent').exclude(user__username=username).update(status='delivered')

    @database_sync_to_async
    def get_room_type(self, room_id):
        try:
            return Room.objects.get(id=room_id).type
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def mark_messages_viewed_if_direct(self, username, room_id):
        room = Room.objects.get(id=room_id)
        if room.type != 'direct':
            return False
        Message.objects.filter(room_id=room_id).exclude(user__username=username).update(status='viewed')
        return True

    @database_sync_to_async
    def mark_all_group_messages_seen(self, username, room_id):
        """Bulk-create MessageRead entries for all unseen messages in a group room."""
        try:
            room = Room.objects.get(id=room_id, type='group')
            user = User.objects.get(username=username)
        except (Room.DoesNotExist, User.DoesNotExist):
            return []
        if not room.participants.filter(id=user.id).exists():
            return []
        # Find all messages by OTHER users that this user hasn't read yet
        unseen_msgs = Message.objects.filter(room=room).exclude(user=user).exclude(reads__user=user)
        results = []
        for msg in unseen_msgs:
            MessageRead.objects.get_or_create(message=msg, user=user)
            seen = list(
                MessageRead.objects.filter(message=msg).values_list('user__username', flat=True).order_by('read_at')
            )
            results.append({'message_id': msg.id, 'seen_by': seen})
        return results

    @database_sync_to_async
    def record_message_seen(self, username, room_id, message_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return None
        if room.type != 'group':
            return None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        if not room.participants.filter(id=user.id).exists():
            return None
        try:
            msg = Message.objects.get(id=message_id, room_id=room_id)
        except Message.DoesNotExist:
            return None
        if msg.user_id == user.id:
            return None
        MessageRead.objects.get_or_create(message=msg, user=user)
        seen = list(
            MessageRead.objects.filter(message=msg).values_list('user__username', flat=True).order_by('read_at')
        )
        return {'message_id': msg.id, 'seen_by': seen}

    @database_sync_to_async
    def get_other_participants(self, current_username, room_id):
        room = Room.objects.get(id=room_id)
        return list(room.participants.exclude(username=current_username).values_list('username', flat=True))
