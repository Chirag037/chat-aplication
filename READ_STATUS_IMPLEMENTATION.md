# Implementation of Message Read Status

This document explains how the "Sent", "Delivered", and "Viewed" status feature was implemented in the chat application.

## 1. Database Schema
The `Message` model in `backend/chat/models.py` was updated to include a `status` field.

- **File**: `backend/chat/models.py`
- **Field**: `status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')`
- **Choices**:
    - `sent`: Message has been created and saved in the database.
    - `delivered`: Message has been received by the recipient's client (WebSocket broadcast received).
    - `viewed`: The recipient has opened the chat room and viewed the message.

## 2. Backend Logic (Django Channels)
The real-time status updates are handled by two consumers in `backend/chat/consumers.py`.

### ChatConsumer
- **`action: mark_read`**: When a user opens a room, they send this action. The backend updates all messages in that room (not sent by the user) to `status='viewed'` and broadcasts a `status_update` to the room.
- **`action: send`**: When a message is sent, the backend sends a notification to other participants' global notification groups to trigger a delivery check.
- **`chat_message` Handler**: When a recipient receives a live broadcast message, their consumer automatically calls `mark_messages_delivered` and sends a `status_update` back to the sender.

### NotificationConsumer
- **Global Delivery Check**: When a user first connects (logs in or refreshes), the `NotificationConsumer` marks all pending `sent` messages addressed to them as `delivered` across all rooms.
- **Real-time Delivery**: It listens for `notify_delivery_check` events to mark specific messages as delivered even if the user isn't currently in the specific chat room.

## 3. Frontend Logic (Vue.js)
The frontend handles the visual representation and triggers status updates.

### Visual Representation
In `fronend/src/views/Chatview.vue`, the message status is rendered with the following icons:
- **Sent** (Single Tick): Default state (opacity 30%).
- **Delivered** (Double Tick): `msg.status === 'delivered'` (opacity 60%).
- **Viewed** (Blue Circle): `msg.status === 'viewed'` (pulsing blue circle).

### Triggering Updates
- **Joining a Room**: When `Chatview.vue` mounts or a room is selected, `markRoomAsRead()` is called, sending `action: mark_read` via WebSocket.
- **Real-time Listening**: The WebSocket `onmessage` handler listens for `type: status_update`. If another user sends a status update, the local `messages` array is updated to reflect the new status (promoting 'sent' to 'delivered' or 'viewed').

## 4. Key Files Involved
1. **Backend Models**: [models.py](file:///home/chirag/office/chat-app/backend/chat/models.py)
2. **WebSocket Consumers**: [consumers.py](file:///home/chirag/office/chat-app/backend/chat/consumers.py)
3. **Frontend View**: [Chatview.vue](file:///home/chirag/office/chat-app/fronend/src/views/Chatview.vue)
