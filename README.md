# 📖 Chat Application — Complete Study Guide

> **Read this before the meeting.** This guide covers every concept, every file,
> and every question your supervisor might ask. It is organized as short,
> numbered chapters. Each chapter ends with a **Q & A section**.

---

## Table of Contents

1. [What Is This Project?](#chapter-1--what-is-this-project)
2. [Tech Stack — Why Each Tool?](#chapter-2--tech-stack--why-each-tool)
3. [Folder Structure Map](#chapter-3--folder-structure-map)
4. [Database Design (Models)](#chapter-4--database-design-models)
5. [Authentication & Security](#chapter-5--authentication--security)
6. [REST API Endpoints](#chapter-6--rest-api-endpoints)
7. [WebSockets — Real-Time Engine](#chapter-7--websockets--real-time-engine)
8. [Message Status Lifecycle (Sent → Delivered → Seen)](#chapter-8--message-status-lifecycle)
9. [Media Sharing & MinIO Storage](#chapter-9--media-sharing--minio-storage)
10. [Frontend Architecture](#chapter-10--frontend-architecture)
11. [How Everything Connects (End-to-End Flows)](#chapter-11--how-everything-connects)
12. [Configuration & Environment](#chapter-12--configuration--environment)
13. [How to Run the Project](#chapter-13--how-to-run-the-project)
14. [Supervisor Meeting — Master Q & A](#chapter-14--supervisor-meeting--master-q--a)

---

---

## Chapter 1 — What Is This Project?

This is a **Real-Time Professional Chat Application**. Think of it like a
simpler version of Slack or WhatsApp Web.

### What can a user do?

- **Register** a new account or **Login** with existing credentials.
- See a list of **Group Rooms** (like Slack channels) and **other users**.
- **Join** a group room or **start a private 1-on-1 chat** (Direct Message).
- **Send text messages** that appear instantly for everyone in the room.
- **Send media files** — images, videos, documents.
- **Edit** or **Delete** their own messages in real-time.
- See **delivery status** — whether a message was Sent, Delivered, or Seen.
- See **"Seen by User A, User B"** labels on group messages.
- **Logout** securely.

### Q & A

**Q: What type of application is this?**
A: A full-stack real-time chat application with direct messaging, group chats,
media sharing, and message status tracking.

**Q: What problem does it solve?**
A: It provides instant communication between team members without needing to
refresh the page. Messages, edits, deletes, and read receipts all appear
in real-time.

**Q: Is it like WhatsApp or Slack?**
A: Yes. It combines features from both — group channels like Slack, and
message delivery/read receipts like WhatsApp.

---

---

## Chapter 2 — Tech Stack — Why Each Tool?

| Technology | Where Used | Why We Chose It |
|:---|:---|:---|
| **Django** | Backend framework | Mature Python framework with built-in ORM, admin panel, and auth system |
| **Django REST Framework (DRF)** | API layer | Makes it easy to create REST API endpoints with serializers and permissions |
| **Django Channels** | WebSocket server | Extends Django to handle long-lived WebSocket connections for real-time features |
| **Daphne** | ASGI server | Required by Channels — replaces the default Django runserver to handle both HTTP and WebSocket |
| **SQLite** | Database | Simple file-based DB, no setup needed for development |
| **Vue 3** | Frontend framework | Reactive UI framework — auto-updates the screen when data changes |
| **Vite** | Build tool / Dev server | Extremely fast development server with hot-reload |
| **Tailwind CSS** | Styling | Utility-first CSS — style directly in HTML without writing separate CSS files |
| **Axios** | HTTP client | Cleaner API calls than native `fetch()`, with interceptors for auth tokens |
| **MinIO** | Media file storage | S3-compatible object storage — stores uploaded images/videos/documents separately from the app server |
| **Docker Compose** | MinIO container | Runs the MinIO server in a container so you don't install it on your machine |
| **JWT (JSON Web Token)** | Authentication | Stateless auth tokens — backend doesn't need sessions, just verifies the token |

### Q & A

**Q: Why Django Channels instead of just Django?**
A: Normal Django handles HTTP only — you send a request, get a response, and
the connection closes. Chat needs a **persistent connection** so the server
can push new messages to the client immediately. Django Channels adds
WebSocket support to Django.

**Q: Why not just use HTTP polling (asking every 2 seconds)?**
A: Polling wastes bandwidth and server resources. With 100 users polling
every 2s, that is 50 requests/second even when nobody is chatting.
WebSockets keep one connection open and only send data when something
actually happens.

**Q: Why MinIO instead of saving files on the server?**
A: Saving files directly on your Django server fills up the disk quickly.
MinIO is a dedicated storage service — files are stored separately and
served via URLs. In production you could swap MinIO for AWS S3 without
changing code.

**Q: Why JWT instead of session cookies?**
A: JWT is stateless — the server doesn't need to store session data.
The token itself contains the user info. This is simpler for
single-page applications (SPA) where the frontend handles routing.

**Q: What is Daphne?**
A: Daphne is the ASGI server that replaces Django's default `runserver`.
It can handle both HTTP and WebSocket connections simultaneously.
Django Channels requires it.

---

---

## Chapter 3 — Folder Structure Map

```
chat-app/
│
├── backend/                    ← Django project root
│   ├── backend/                ← Django project config
│   │   ├── settings.py         ← All configuration (DB, JWT, MinIO, Channels)
│   │   ├── urls.py             ← All HTTP URL routes (/api/login, /api/messages, etc.)
│   │   ├── asgi.py             ← Entry point: routes HTTP vs WebSocket traffic
│   │   └── wsgi.py             ← Standard WSGI (not used when Channels is active)
│   │
│   ├── chat/                   ← Main Django app
│   │   ├── models.py           ← Database tables (Room, Message, MessageRead)
│   │   ├── views.py            ← REST API handlers (register, login, messages, rooms)
│   │   ├── serializers.py      ← Convert DB objects ↔ JSON
│   │   ├── consumers.py        ← WebSocket handlers (ChatConsumer, NotificationConsumer)
│   │   └── routing.py          ← WebSocket URL patterns
│   │
│   ├── db.sqlite3              ← The database file
│   ├── manage.py               ← Django CLI tool
│   └── requirements.txt        ← Python dependencies
│
├── fronend/                    ← Vue.js frontend (note: "fronend" not "frontend")
│   ├── src/
│   │   ├── api.js              ← Axios HTTP client with JWT interceptor
│   │   ├── router/index.js     ← Vue Router (defines /login and /chat pages)
│   │   ├── views/
│   │   │   ├── Loginview.vue   ← Login & Register page
│   │   │   └── Chatview.vue    ← Main chat page (largest file — all chat logic)
│   │   └── components/
│   │       └── Sidebar.vue     ← Left sidebar (rooms, users, channels list)
│   │
│   ├── vite.config.js          ← Dev server config + proxy settings
│   └── package.json            ← Node.js dependencies
│
├── docker-compose.yml          ← Runs MinIO storage server
└── minio_data/                 ← MinIO stored files (auto-created)
```

### Q & A

**Q: Why is the frontend folder named "fronend" instead of "frontend"?**
A: It is a typo made during initial project creation. Renaming it now
would break references, so we kept it as-is.

**Q: Which file should I open first to understand the project?**
A: Start with `backend/chat/models.py` (the database), then `views.py`
(the API), then `consumers.py` (real-time), then the Vue files.

**Q: Where is the database?**
A: It is the file `backend/db.sqlite3`. SQLite stores everything in a
single file — no separate database server needed.

---

---

## Chapter 4 — Database Design (Models)

File: `backend/chat/models.py`

We have **3 tables** (models):

### Table 1: `Room`

```
┌──────────────────────────────────────────────────────┐
│ Room                                                 │
├──────────────┬───────────────────────────────────────┤
│ id           │ Auto-generated primary key             │
│ name         │ Room name (e.g. "General") — optional  │
│ type         │ "group" OR "direct"                    │
│ participants │ Many-to-Many → User table              │
└──────────────┴───────────────────────────────────────┘
```

- A **group** room has a name and many participants.
- A **direct** room has no name and exactly 2 participants.

### Table 2: `Message`

```
┌──────────────────────────────────────────────────────┐
│ Message                                              │
├──────────────┬───────────────────────────────────────┤
│ id           │ Auto-generated primary key             │
│ user         │ Foreign Key → User (who sent it)       │
│ room         │ Foreign Key → Room (which room)        │
│ content      │ Text body of the message               │
│ status       │ "sent" / "delivered" / "viewed"         │
│ message_type │ "text" / "image" / "video" / "file"    │
│ attachment   │ File field → stored in MinIO            │
│ created_at   │ Timestamp (auto-set on creation)       │
└──────────────┴───────────────────────────────────────┘
```

- Messages are ordered by `created_at` (oldest first).
- The `status` field tracks delivery lifecycle.
- The `attachment` field stores the file URL in MinIO.

### Table 3: `MessageRead`

```
┌──────────────────────────────────────────────────────┐
│ MessageRead (Read Receipts — group chats only)       │
├──────────────┬───────────────────────────────────────┤
│ id           │ Auto-generated primary key             │
│ message      │ Foreign Key → Message                  │
│ user         │ Foreign Key → User (who read it)       │
│ read_at      │ Timestamp (when they read it)          │
└──────────────┴───────────────────────────────────────┘
│ CONSTRAINT: One user can only read a message once     │
└───────────────────────────────────────────────────────┘
```

- This table stores **"User X read Message Y at Time Z"**.
- The unique constraint prevents duplicate entries.
- Used to display **"Seen by Alice, Bob"** in group chats.

### Bonus: `cleanup_orphaned_rooms` (Signal)

When a user is **deleted**, this signal automatically removes any direct
rooms that would have less than 2 participants (broken rooms).

### Q & A

**Q: Why do we need a separate `MessageRead` table? Why not just put
"seen_by" in the Message table?**
A: Because in a group room with 10 people, each person reads the message
at a different time. We need to track **who** read it and **when**.
A separate table allows one row per user per message.

**Q: Why does `Message.status` exist if we also have `MessageRead`?**
A: They serve different purposes:
- `status` is a quick field for **direct messages** (sent → delivered → viewed).
- `MessageRead` is for **group messages** where we need to track each reader individually.

**Q: What is a Many-to-Many relationship?**
A: Room has `participants = ManyToManyField(User)`. This means one room
can have many users, and one user can be in many rooms. Django
automatically creates a junction table to link them.

**Q: What is `auto_now_add=True`?**
A: It automatically sets the field to the current time when the row is
first created. You don't need to pass it manually.

**Q: What is `on_delete=models.CASCADE`?**
A: If the parent object (e.g., a User) is deleted, all their Messages
are also deleted automatically. "CASCADE" means "delete everything
connected to it."

---

---

## Chapter 5 — Authentication & Security

### How Login Works (Step by Step)

```
1. User enters username + password on Loginview.vue
2. Frontend sends POST /api/login/ with { username, password }
3. views.py → login() → authenticate(username, password)
4. If valid → generate JWT tokens (access + refresh)
5. Return { access: "eyJ...", refresh: "eyJ..." }
6. Frontend stores access_token in localStorage
7. Redirect user to /chat page
```

### How Every API Call Is Secured

```
1. User wants to fetch messages → GET /api/messages/
2. api.js interceptor reads localStorage('access_token')
3. Attaches header: Authorization: Bearer eyJ...
4. Django receives request → JWTAuthentication middleware verifies token
5. If valid → request.user is set → view executes
6. If expired/invalid → 401 Unauthorized → frontend redirects to /login
```

### How Registration Works

```
1. User fills username + password + confirm password
2. Frontend sends POST /api/register/
3. views.py → register() → creates User → generates JWT
4. Return tokens → auto-login → redirect to /chat
```

### Q & A

**Q: What is a JWT token?**
A: JSON Web Token — a long encoded string like `eyJhbGciOi...`. It contains
the user's ID and an expiry time. The server signs it with a secret key
so nobody can fake it.

**Q: Where is the token stored?**
A: In the browser's `localStorage` under the key `access_token`.

**Q: What happens if the token expires?**
A: The API returns 401 Unauthorized. The `api.js` response interceptor
catches this, clears localStorage, and redirects to `/login`.

**Q: How long does the token last?**
A: Access token: **7 days**. Refresh token: **14 days**.
(Configured in `settings.py` under `SIMPLE_JWT`)

**Q: What are the public endpoints that don't need a token?**
A: `/api/login/`, `/api/register/`, and `/api/health/`. All others
require authentication.

---

---

## Chapter 6 — REST API Endpoints

File: `backend/backend/urls.py` and `backend/chat/views.py`

| Method | Endpoint | Auth? | What It Does |
|:------:|:---------|:-----:|:-------------|
| POST | `/api/register/` | No | Create new user, return JWT tokens |
| POST | `/api/login/` | No | Verify credentials, return JWT tokens |
| GET | `/api/users/` | Yes | List all other users (for starting DMs) |
| GET | `/api/rooms/` | Yes | List your direct message rooms |
| GET | `/api/rooms/group/` | Yes | List all group rooms (auto-creates "General") |
| POST | `/api/rooms/join/` | Yes | Join a group room by `room_id` |
| POST | `/api/rooms/direct/` | Yes | Create/find a DM room with another user |
| GET | `/api/messages/?room_id=X` | Yes | Get all messages in a room |
| POST | `/api/messages/` | Yes | Send a new message (used for media uploads) |
| GET | `/api/health/` | No | Health check (returns `{"status": "ok"}`) |

### How the Catch-All Route Works

```python
# In urls.py — this line at the bottom:
re_path(r'^(?!api/|admin/|static/).*', TemplateView.as_view(template_name='index.html'))
```

This means: **any URL that doesn't start with `/api/`, `/admin/`, or `/static/`
gets served the Vue `index.html`**. This is how Vue Router handles `/login`
and `/chat` — Django doesn't care about those routes, it just serves the
Vue app and lets Vue handle the routing.

### Q & A

**Q: Why do we need both REST API and WebSockets?**
A: REST API handles: login, register, loading message history, creating rooms.
WebSockets handle: real-time message sending, editing, deleting, status updates.
They complement each other.

**Q: Why is message sending done through WebSocket AND REST?**
A: Text messages use WebSocket for speed (already connected, no HTTP overhead).
Media files use REST because WebSockets can't handle large binary file uploads.
If the WebSocket is temporarily down, text also falls back to REST.

**Q: What does `get_or_create` do in `list_group_rooms`?**
A: It checks if a "General" room exists. If yes, returns it. If no, creates
it. This ensures the General room always exists without duplicate errors.

**Q: What does the POST /api/messages/ endpoint do after saving?**
A: After saving the message to the database, it also **broadcasts it through
the WebSocket channel** so all connected users see it instantly. It uses
`get_channel_layer()` to access the Channels system from a REST view.

---

---

## Chapter 7 — WebSockets — Real-Time Engine

Files: `backend/chat/consumers.py` and `backend/chat/routing.py`

### What Is a WebSocket?

```
HTTP (Normal):
  Client ──request──► Server
  Client ◄──response── Server
  Connection CLOSES.

WebSocket:
  Client ◄──────────► Server
  Connection STAYS OPEN.
  Either side can send data at any time.
```

### WebSocket URLs (routing.py)

```
ws/chat/<room_id>/     →  ChatConsumer     (handles one chat room)
ws/notifications/      →  NotificationConsumer  (handles delivery tracking)
```

### How the Server Routes WebSocket vs HTTP (asgi.py)

```python
application = ProtocolTypeRouter({
    "http": get_asgi_application(),          # Normal Django
    "websocket": AuthMiddlewareStack(        # WebSocket → Channels
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
```

Every incoming connection first hits `asgi.py`. If it is HTTP → Django
handles it normally. If it is WebSocket → Channels routes it to the
correct consumer.

### Consumer 1: `ChatConsumer`

This handles the **active chat room** the user is looking at.

**Actions the frontend can send:**

| Action | What Happens |
|:-------|:-------------|
| `join` | Binds the username to this socket. Marks pending messages as "delivered". |
| `send` | Saves message to DB. Broadcasts to all participants. Pings NotificationConsumer for delivery tracking. |
| `delete` | Deletes message from DB (only if sender matches). Broadcasts deletion to all. |
| `edit` | Updates message content in DB. Broadcasts edit to all. |
| `mark_read` | For **direct** rooms: marks all others' messages as "viewed". For **group** rooms: creates `MessageRead` entries. |
| `mark_message_seen` | For **group** rooms only: creates one `MessageRead` entry for a specific message. Broadcasts "read_receipt". |

**Events the server broadcasts to the room:**

| Event | When | What the Frontend Does |
|:------|:-----|:-----------------------|
| `chat_message` | New message sent | Add bubble to the chat |
| `status_update` | Delivery/viewed status changed | Update tick icons (✓ ✓✓ 🔵) |
| `message_deleted` | Someone deleted a message | Remove the bubble |
| `message_edited` | Someone edited a message | Update bubble text, show "Edited" |
| `read_receipt` | Someone read a group message | Update "Seen by..." label |

### Consumer 2: `NotificationConsumer`

This runs **globally** — it is connected the moment the user opens the app,
regardless of which room they are in.

**Purpose:** Detect if a user is online. When they are, mark pending
messages as "Delivered".

**How it works:**
1. User opens the app → `Chatview.vue` connects to `ws/notifications/`.
2. Sends `{action: "join", username: "chirag"}`.
3. Consumer subscribes to group `notify_chirag`.
4. Calls `mark_all_as_delivered("chirag")` → bulk-updates all "sent" messages in all rooms where chirag is a participant.
5. Later, when someone sends a message, `ChatConsumer` pings `notify_chirag` with a `notify_delivery_check` event.
6. `NotificationConsumer` receives it, marks that specific message as "delivered", and broadcasts the status update.

### Q & A

**Q: What is a "Channel Layer"?**
A: It is the communication bus between consumers. When Consumer A wants
to send a message to Consumer B, it uses the channel layer. Think of it
like a message queue connecting all WebSocket handlers.

**Q: What does `InMemoryChannelLayer` mean?**
A: Messages between consumers are stored in RAM. This works fine for
development but doesn't work with multiple server processes. In
production, you'd use Redis as the channel layer.

**Q: What is `@database_sync_to_async`?**
A: Django's ORM is synchronous (blocking). WebSocket consumers are async
(non-blocking). This decorator wraps synchronous DB calls so they can
be used inside async consumers without freezing the server.

**Q: Why do we need TWO consumers?**
A: `ChatConsumer` handles one specific room. `NotificationConsumer` handles
all rooms at once. A user might not be in any chat room but still online.
The notification consumer tracks their online status to mark messages
as delivered.

**Q: What is `group_send`?**
A: It sends a message to ALL consumers subscribed to a group name.
For example, `group_send("chat_5", ...)` sends to everyone in Room 5.

**Q: What is the `type` field in `group_send`?**
A: It tells which method to call on the receiving consumer. For example,
`type: "chat_message"` calls the `chat_message()` method on the consumer.
Django Channels converts underscores to dots internally.

---

---

## Chapter 8 — Message Status Lifecycle

### Visual Diagram

```
  SENT                   DELIVERED                 VIEWED
   ✓                       ✓✓                       🔵
   │                        │                         │
 Message saved         Recipient is              Recipient opened
 to database.          online (connected          the chat room and
                       to notification            actually looked at
                       socket).                   the message.
```

### How Status Changes — Direct Messages

```
Step 1: User A sends message → status = "sent" (saved to DB)
Step 2: ChatConsumer broadcasts to room group
Step 3: If User B is connected to this room → ChatConsumer marks "delivered"
Step 4: If User B is online but in different room → NotificationConsumer marks "delivered"
Step 5: User B opens the room → Chatview sends {action: "mark_read"}
Step 6: ChatConsumer bulk-updates all messages to "viewed"
Step 7: status_update event sent → User A sees 🔵 icon
```

### How Status Changes — Group Messages

```
Step 1: User A sends message → status = "sent"
Step 2: User B opens the room → Chatview sends {action: "mark_message_seen", message_id: 42}
Step 3: ChatConsumer creates MessageRead row (message=42, user=B)
Step 4: Broadcasts read_receipt with seen_by: ["UserB"]
Step 5: User C also reads it → MessageRead row for User C
Step 6: Broadcasts read_receipt with seen_by: ["UserB", "UserC"]
Step 7: User A's UI shows "Seen by UserB, UserC" under the message
```

### Frontend Status Icons (`Chatview.vue`)

```
status = "sent"      → Single grey tick     ✓
status = "delivered"  → Double grey ticks    ✓✓
status = "viewed"     → Blue filled circle   🔵
seen_by.length > 0    → Blue circle + names  🔵 Seen by Alice, Bob
```

### Q & A

**Q: Can a message go from "viewed" back to "delivered"?**
A: No. The code explicitly prevents downgrading. In `Chatview.vue`:
```
if (data.status === 'viewed' && m.status !== 'viewed') → upgrade
if (data.status === 'delivered' && m.status === 'sent') → upgrade
```
It only upgrades statuses, never downgrades.

**Q: What is the difference between `mark_read` and `mark_message_seen`?**
A: `mark_read` is a **bulk** action — marks ALL messages in the room.
`mark_message_seen` targets a **single specific** message by ID.

**Q: Why does the "Seen by" feature only work in group rooms?**
A: In direct rooms, there's only one other person — you either saw it or
didn't. The `status` field (viewed) is enough. In group rooms, we need
to know WHICH users out of many saw it, hence `MessageRead`.

---

---

## Chapter 9 — Media Sharing & MinIO Storage

### What Is MinIO?

MinIO is a **self-hosted object storage server**. It is compatible with
Amazon S3 APIs. We run it using Docker.

### How MinIO Runs

```bash
# docker-compose.yml starts MinIO:
docker compose up -d

# MinIO runs on:
# Port 9000 → API (Django uploads/downloads here)
# Port 9001 → Web Console (you can browse files in browser)
# Login: minioadmin / minioadmin
```

### How File Upload Works (Step by Step)

```
1. User clicks the "+" button in Chatview.vue
   → triggers file picker (hidden <input type="file">)

2. User selects a file (e.g., photo.jpg)
   → stored in this.selectedFile

3. User presses Enter or clicks Send
   → sendMessage() detects selectedFile is not null
   → builds FormData:
       formData.append('room', roomId)
       formData.append('content', 'optional caption')
       formData.append('attachment', the_file)
       formData.append('message_type', 'image')  ← auto-detected

4. POST /api/messages/ with multipart/form-data
   → Django receives the file via request.FILES['attachment']

5. Django saves Message to DB
   → attachment field uses S3Storage backend
   → file is uploaded to MinIO bucket "media"
   → URL like: http://localhost:9000/media/chat_attachments/photo.jpg

6. Django broadcasts via WebSocket:
   { type: chat_message, attachment: "http://...", message_type: "image" }

7. All participants receive the broadcast
   → Chatview.vue renders:
       Image? → <img> tag with zoom-on-click
       Video? → <video> tag with controls
       Other? → File card with download button
```

### Django Storage Configuration (settings.py)

```python
AWS_S3_ENDPOINT_URL = 'http://localhost:9000'   # MinIO server
AWS_STORAGE_BUCKET_NAME = 'media'                # Bucket name
AWS_ACCESS_KEY_ID = 'minioadmin'                 # Credentials
AWS_SECRET_ACCESS_KEY = 'minioadmin'

STORAGES = {
    "default": {"BACKEND": "storages.backends.s3.S3Storage"},  # Files → MinIO
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}
```

### Q & A

**Q: Why not send files through WebSocket?**
A: WebSockets are designed for small text/JSON messages. Sending a 10MB
video over WebSocket would block the connection and could fail silently.
HTTP multipart upload is designed for file transfers.

**Q: Where are the files physically stored?**
A: In the `minio_data/` directory on your machine. MinIO maps its internal
`/data` to `./minio_data` via Docker volume mount.

**Q: What if MinIO is not running?**
A: File uploads will fail with a connection error. Text-only messages
will still work fine.

**Q: How does the frontend know if a message is an image or a video?**
A: The `message_type` field on the Message model. The frontend checks
`msg.message_type` and renders the appropriate HTML element.

---

---

## Chapter 10 — Frontend Architecture

### Page Flow

```
User opens app
    │
    ▼
router/index.js checks route
    │
    ├── /login  →  Loginview.vue
    ├── /chat   →  Chatview.vue
    └── /       →  redirect to /login
```

### File: `api.js` — The HTTP Client

**What it does:** Creates an Axios instance that automatically:
1. Attaches JWT token to every request header.
2. Redirects to `/login` if the server returns 401.

**Key code:**
```javascript
// Before every request:
if (token && !isPublic) {
    config.headers['Authorization'] = `Bearer ${token}`;
}

// After every response:
if (status === 401) {
    localStorage.clear();
    window.location.href = '/login';
}
```

### File: `Loginview.vue` — Login Page

**What it does:**
- Shows login form (switches to register on click).
- Validates passwords match (for registration).
- Sends POST to `/api/login/` or `/api/register/`.
- Stores `access_token` and `username` in localStorage.
- Redirects to `/chat` after 1.2 seconds.

### File: `Sidebar.vue` — Navigation Panel

**What it does:**
- On mount, fetches 3 API calls in parallel:
  - `GET /api/rooms/group/` → Group channels.
  - `GET /api/rooms/` → Your direct message rooms.
  - `GET /api/users/` → All other users.
- Refreshes every 5 seconds (polling for new rooms/users).
- Click a group room → auto-joins if not a member, then emits `select-room`.
- Click a user → creates/finds a direct room, then emits `select-room`.

### File: `Chatview.vue` — The Main Chat Engine (Largest File)

This is the **heart of the frontend**. It manages:

**Data State:**
```
messages[]       → Array of message objects for current room
roomId           → Currently active room ID
currentUser      → Logged-in username (from localStorage)
socket           → WebSocket for current chat room
notifySocket     → WebSocket for delivery notifications (global)
selectedFile     → File waiting to be sent
editingMessageId → ID of message being edited (null if not editing)
lightboxImage    → URL of image being viewed fullscreen (null if not viewing)
```

**Key Methods:**
| Method | What It Does |
|:-------|:-------------|
| `handleRoomSelect(room)` | Switch to a new room — close old socket, fetch messages, open new socket |
| `initWebSocket()` | Connect to `ws/chat/<roomId>/`, send "join", start listening for events |
| `initNotificationSocket()` | Connect to `ws/notifications/`, send "join" — runs globally |
| `sendMessage()` | If file attached → POST API. If text only → WebSocket send. |
| `deleteMessage(id)` | Send "delete" via WebSocket. Remove from local array immediately. |
| `startEdit(msg)` / `saveEdit()` | Show inline edit textarea. Send "edit" via WebSocket. |
| `markRoomAsRead()` | Send "mark_read" via WebSocket when entering a room |
| `fetchMessages()` | GET /api/messages/?room_id=X to load chat history |

**WebSocket Event Handling (inside `socket.onmessage`):**
```
Received "message"       → Push new bubble to messages[]
Received "delete"        → Remove bubble by ID
Received "edit"          → Update bubble content, mark as edited
Received "status_update" → Update tick icons (sent→delivered→viewed)
Received "read_receipt"  → Update "Seen by..." label on specific message
```

### File: `vite.config.js` — Development Proxy

```javascript
proxy: {
    '/api': { target: 'http://localhost:8000' },   // API calls → Django
    '/ws':  { target: 'ws://localhost:8000', ws: true }  // WebSocket → Django
}
```

The Vue dev server runs on port 5173. Django runs on port 8000.
The proxy makes them appear like the same origin so there are
no CORS issues in development.

### Q & A

**Q: Why does Sidebar poll every 5 seconds instead of using WebSocket?**
A: The sidebar shows rooms and users across the whole app. Using a
WebSocket just for room list updates would add complexity for small
benefit. Polling every 5s is simple and sufficient.

**Q: What happens if the WebSocket disconnects?**
A: `sendMessage()` has a fallback — if `socket.readyState !== OPEN`,
it uses `POST /api/messages/` instead. The notification socket
auto-reconnects after 3 seconds.

**Q: What is the lightbox feature?**
A: When you click an image in chat, it opens a fullscreen overlay
showing the image with a download button. Press Escape to close.

**Q: Why does `handleRoomSelect` close the old socket?**
A: Each room has its own WebSocket connection. When you switch rooms,
you must disconnect from the old room's channel and connect to the
new one. Otherwise you'd receive messages from the wrong room.

---

---

## Chapter 11 — How Everything Connects

### Complete Flow: User Opens App and Sends a Message

```
┌─────────────────────────────────────────────────────────────────┐
│                        STARTUP PHASE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. User opens browser → http://localhost:5173                  │
│  2. Vue Router sees "/" → redirects to "/login"                 │
│  3. Loginview.vue renders login form                            │
│  4. User submits credentials                                   │
│  5. POST /api/login/ → Django verifies → returns JWT            │
│  6. Token saved to localStorage                                 │
│  7. Vue Router navigates to "/chat"                             │
│  8. Chatview.vue mounted() runs:                                │
│     a. Checks localStorage for token (if missing → /login)     │
│     b. Connects notifySocket → ws/notifications/                │
│     c. If last_room_id exists → fetch messages + init socket    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     ROOM SELECTION PHASE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  9. Sidebar.vue loads (fetches rooms + users via API)           │
│ 10. User clicks "General" group room                            │
│ 11. Sidebar calls selectGroupRoom() → POST /api/rooms/join/    │
│ 12. Emits select-room event to Chatview                        │
│ 13. Chatview.handleRoomSelect():                               │
│     a. Sets roomId = (selected room ID)                        │
│     b. GET /api/messages/?room_id=X → loads history             │
│     c. Closes old WebSocket (if any)                            │
│     d. Opens new WebSocket → ws/chat/<room_id>/                 │
│     e. Sends {action: "join", username: "chirag"}               │
│     f. Sends {action: "mark_read"} → marks messages as seen    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     MESSAGE SENDING PHASE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 14. User types "Hello" and presses Enter                        │
│ 15. sendMessage() runs                                          │
│ 16. Socket is open → sends JSON:                                │
│     { action: "send", message: "Hello", username: "chirag" }   │
│ 17. ChatConsumer.receive() on server:                           │
│     a. Parses JSON                                              │
│     b. save_message() → creates Message row in DB               │
│     c. group_send("chat_5", { type: "chat_message", ... })     │
│     d. For each other participant → pings notify_<username>     │
│ 18. All consumers in "chat_5" receive chat_message event        │
│ 19. Each consumer sends JSON to their WebSocket client          │
│ 20. Each client's Chatview.vue receives via socket.onmessage    │
│ 21. New message pushed to messages[] → renders as chat bubble   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Q & A

**Q: How many WebSocket connections does one user have?**
A: **Two.** One to `ws/notifications/` (always open), and one to
`ws/chat/<room_id>/` (for the currently active room).

**Q: What happens when the server restarts?**
A: All WebSocket connections drop. The notification socket auto-reconnects
after 3 seconds. The chat socket needs the user to switch rooms or
refresh the page.

---

---

## Chapter 12 — Configuration & Environment

File: `backend/backend/settings.py`

### Key Configuration Blocks

| Setting | Value | Purpose |
|:--------|:------|:--------|
| `ASGI_APPLICATION` | `backend.asgi.application` | Tells Daphne which file to use as entry point |
| `CHANNEL_LAYERS` | `InMemoryChannelLayer` | How consumers communicate (in-memory for dev) |
| `SIMPLE_JWT.ACCESS_TOKEN_LIFETIME` | 7 days | How long the login token lasts |
| `CORS_ALLOW_ALL_ORIGINS` | True (dev only) | Allows frontend on port 5173 to call API on port 8000 |
| `REST_FRAMEWORK.DEFAULT_AUTHENTICATION` | `JWTAuthentication` | All API endpoints use JWT by default |
| `STORAGES.default` | `S3Storage` | File uploads go to MinIO instead of local filesystem |
| `AWS_S3_ENDPOINT_URL` | `http://localhost:9000` | Where MinIO is running |

### Q & A

**Q: What would need to change for production?**
A: 1) Change `InMemoryChannelLayer` to Redis. 2) Set `DEBUG = False`.
3) Set `CORS_ALLOW_ALL_ORIGINS = False`. 4) Set a real `SECRET_KEY`.
5) Replace SQLite with PostgreSQL. 6) Point MinIO to a real S3 service.

---

---

## Chapter 13 — How to Run the Project

### Step 1: Start MinIO (for media uploads)

```bash
cd chat-app
docker compose up -d
```

### Step 2: Start Backend

```bash
cd backend
source ../venv/bin/activate
pip install -r requirements.txt   # first time only
python manage.py migrate           # first time only
python manage.py runserver
```

### Step 3: Start Frontend

```bash
cd fronend
npm install     # first time only
npm run dev
```

### Step 4: Open in Browser

```
http://localhost:5173
```

---

---

## Chapter 14 — Supervisor Meeting — Master Q & A

These are the most likely questions a supervisor would ask, with
prepared answers.

---

### Architecture & Design

**Q: Explain the architecture in one sentence.**
A: It is a Django REST + Django Channels backend serving a Vue 3 SPA,
with two WebSocket channels for real-time chat and delivery notifications,
and MinIO for media storage.

**Q: Why did you separate chat and notifications into two WebSocket connections?**
A: The chat socket is room-specific — it changes when you switch rooms.
The notification socket is global — it tracks online status across all
rooms. Combining them would make room switching lose delivery tracking.

**Q: How do the frontend and backend communicate?**
A: Through two channels:
1. **HTTP/REST** — for login, register, loading data, uploading files.
2. **WebSocket** — for real-time messaging, edits, deletes, status updates.

**Q: Why is SQLite acceptable here?**
A: For development and small teams, SQLite is fast and needs no setup.
For production with many concurrent users, we would migrate to PostgreSQL.

---

### Real-Time Features

**Q: How does a message appear instantly without refreshing?**
A: WebSocket. The browser keeps a persistent connection to the server.
When one user sends a message, the server broadcasts it to all connected
users in that room. Their Vue.js reactivity system automatically
renders the new message.

**Q: What happens if two people send a message at the exact same time?**
A: Both messages are saved to the database with different timestamps.
Both are broadcast to the room group. Every client receives both and
appends them in order. No conflict.

**Q: How do you prevent a user from deleting/editing another user's message?**
A: The `delete_message()` and `edit_message()` functions in `consumers.py`
both filter by `user__username=username`. If the sender doesn't match,
the query returns nothing and the action is silently ignored.

---

### Security

**Q: How is the API secured?**
A: Every protected endpoint requires a valid JWT token in the
`Authorization: Bearer <token>` header. The token is issued on login
and verified on each request by DRF's `JWTAuthentication` class.

**Q: Can someone access a room they're not part of?**
A: No. The `messages()` view filters by `participants=request.user`.
If you're not a participant, you get a 403 Forbidden error.

**Q: What happens if someone tampers with the JWT token?**
A: The token is cryptographically signed with `SECRET_KEY`. Any
modification invalidates the signature, and the server rejects it.

---

### Database

**Q: How many tables does the app use?**
A: Three custom tables: `Room`, `Message`, and `MessageRead`. Plus
Django's built-in `User` table for authentication.

**Q: What is the relationship between Room and User?**
A: Many-to-Many. One room has many participants, one user can be in
many rooms. Django creates a hidden join table `chat_room_participants`
to manage this.

**Q: How does the "Seen by" feature work in the database?**
A: Each time a user reads a message, a `MessageRead` row is created
linking that user to that message. To show "Seen by Alice, Bob", we
query all `MessageRead` rows for that message and list the usernames.

---

### Media & Storage

**Q: How do file uploads work?**
A: The frontend sends a multipart form via HTTP POST. Django receives the
file, Django's storage backend (configured as S3Storage) automatically
uploads it to MinIO. The file URL is saved in the database and broadcast
to all chat participants via WebSocket.

**Q: What file types are supported?**
A: Images (rendered inline with zoom), Videos (rendered with player controls),
and all other files (rendered as a downloadable card with icon).

---

### Deployment & Scalability

**Q: What would you change for production deployment?**
A: Five changes:
1. Replace `InMemoryChannelLayer` with **Redis** (supports multiple workers).
2. Replace **SQLite** with **PostgreSQL** (handles concurrent writes).
3. Set `DEBUG = False` and use a real `SECRET_KEY`.
4. Use **Nginx** as reverse proxy in front of Daphne.
5. Either keep MinIO or switch to **AWS S3** (no code changes needed).

**Q: Can this handle 1000 users?**
A: With the current setup (SQLite + InMemoryChannelLayer), no. With
PostgreSQL + Redis + multiple Daphne workers behind Nginx, yes.

---

### Code Quality

**Q: What design patterns are used?**
A: 1) **MVC pattern** — Models in `models.py`, Views in `views.py`,
Templates in Vue components. 2) **Observer pattern** — WebSocket consumers
listen for and broadcast events. 3) **Interceptor pattern** — Axios
interceptors automatically attach auth tokens.

**Q: How is the code organized?**
A: Clean separation: Models handle data, Views handle HTTP logic,
Consumers handle WebSocket logic, Serializers handle data transformation,
Vue components handle UI rendering. Each file has one clear responsibility.

---

> **Final tip for the meeting:** If your supervisor asks something you're
> unsure about, refer them to the specific file. Every feature maps
> to a specific file in this guide. Knowing *where* the code lives
> is just as impressive as knowing *how* it works.
