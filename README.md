# Real-Time Professional Chat App

A sleek, minimalist chat application designed for professional communication. Built with **Django Channels** and **Vue 3**.

## ✨ Features
- **Real-Time Communication**: Instant messaging powered by WebSockets.
- **Message CRUD**: Full support for Editing and Deleting your own messages.
- **Versatile Rooms**: Support for both Public Group Rooms and Private 1-on-1 Direct Messages.
- **Professional UI**: A neutral, high-end "Linear-style" design using Tailwind CSS.
- **Reliable Auth**: Secure login and session management.

## 🚀 Quick Start

### 1. Backend (Django)
```bash
cd backend
python -m venv ../venv
source ../venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Frontend (Vue 3)
```bash
cd fronend
npm install
npm run dev
```

## 🛠️ Tech Stack
- **Backend**: Python, Django, Django Channels, Daphne.
- **Frontend**: Vue 3 (Vite), Tailwind CSS, Axios.
- **Database**: SQLite.

## ⚙️ Configuration (env)

Backend settings read optional environment variables:

- **`DJANGO_SECRET_KEY`**: Django secret key (required in production)
- **`DJANGO_DEBUG`**: `true` / `false`
- **`DJANGO_ALLOWED_HOSTS`**: comma-separated list
- **`CORS_ALLOWED_ORIGINS`**: comma-separated list

You can copy `backend/.env.example` to `backend/.env` and set values.

## 📚 Codebase guide (how it works)

This repo is a **Django + Django REST Framework + Channels (WebSockets)** backend with a **Vue 3 + Vue Router + Vite + Tailwind** frontend. Users **register/login**, get **JWT** access tokens, join **group** rooms (e.g. **General**) and **direct** chats, send **messages** over **WebSockets** (with REST fallback), and track **delivery / viewed** on `Message` plus **per-user read receipts** (`MessageRead`) in **group** rooms.

### Folder layout (what to open first)

| Path | Role |
|------|------|
| `backend/backend/` | Django project: `settings.py`, `urls.py`, `asgi.py` (HTTP + WebSockets) |
| `backend/chat/` | App: **models**, **views**, **serializers**, **consumers** (WS), **routing** (WS URLs) |
| `fronend/src/` | Vue app (note the folder name **`fronend`**) |
| `fronend/vite.config.js` | Dev server + **proxy** for `/api` and `/ws` → Django |
| `venv/` | Python env (ignore for “understanding” the app logic) |

### How requests flow

1. **HTTP (REST)**
   - Browser hits `window.location.origin` (Vite dev proxies `/api` to port 8000).
   - `backend/backend/urls.py` maps paths like `/api/login/`, `/api/messages/`, `/api/rooms/group/`, etc.
   - Protected routes use **`Authorization: Bearer <JWT>`** (see `fronend/src/api.js`).

2. **WebSockets**
   - `backend/backend/asgi.py` wires **HTTP** to Django and **WebSocket** to `chat.routing.websocket_urlpatterns`.
   - Two consumers: **per-room chat** `ws/chat/<room_id>/`, and **notifications** `ws/notifications/`.
   - Channel layer is **in-memory** (`settings.CHANNEL_LAYERS`), fine for single-process dev.

3. **SPA**
   - Non-API routes serve `index.html` so Vue Router handles `/chat`, `/login` (`backend/backend/urls.py` catch-all).

### Backend: important files and what they do

#### `backend/chat/models.py`

- **`Room`**: `type` = `group` or `direct`; `participants` M2M to `User`; optional `name`.
- **`Message`**: belongs to `User` + `Room`; `content`, `status` (`sent` / `delivered` / `viewed`), `created_at`.
- **`MessageRead`**: **who read which message** (used for **group** “seen by” lists); unique `(message, user)`.
- **`cleanup_orphaned_rooms`**: signal on `User` delete — removes broken **direct** rooms with < 2 participants.

#### `backend/chat/serializers.py`

- **`UserSerializer`**, **`RoomSerializer`** (with participants).
- **`MessageSerializer`**: exposes `username`, **`seen_by`** (from `MessageRead` for group rooms), **`room_type`**.

#### `backend/chat/views.py` (main HTTP handlers)

- **`register` / `login`**: create user or authenticate; return **JWT** (`RefreshToken`).
- **`list_users`**: other users for starting DMs.
- **`room_list`**: **direct** rooms for current user (with 2 participants).
- **`list_group_rooms`**: all **group** rooms; ensures **General** exists.
- **`join_group_room`**: add current user as **participant** on a group room.
- **`create_direct_room`**: find-or-create **direct** room between two users.
- **`messages`**: **GET** history (must be a **participant**); **POST** create message (REST path).

#### `backend/chat/consumers.py` (WebSocket logic)

- **`NotificationConsumer`** (`/ws/notifications/`): client sends `join` + `username` → subscribes to `notify_<username>`. Used so when someone sends a chat message, **other users’** sockets can run **`notify_delivery_check`** → mark message **delivered** and fan out **`status_update`** to the room. Also **`mark_all_as_delivered`** on join for pending “sent” messages.

- **`ChatConsumer`** (`/ws/chat/<room_id>/`):
  - Joins Channels group `chat_<room_id>`.
  - **`receive`** handles JSON actions: **`join`**, **`send`**, **`delete`**, **`edit`**, **`mark_read`** (direct-only bulk “viewed” on `Message.status`), **`mark_message_seen`** (group read receipts → **`MessageRead`** + broadcast **`read_receipt`**).
  - Group event handlers: **`chat_message`**, **`status_update`**, **`message_deleted`**, **`message_edited`**, **`read_receipt`**.
  - DB work uses **`@database_sync_to_async`** wrappers.

#### `backend/chat/routing.py`

- Maps URL patterns to **`ChatConsumer`** and **`NotificationConsumer`**.

#### `backend/backend/asgi.py`

- **`ProtocolTypeRouter`**: `"http"` → Django ASGI app; `"websocket"` → **`AuthMiddlewareStack`** + **`URLRouter(chat.routing.websocket_urlpatterns)`**.

### Frontend: important files and what they do

#### `fronend/src/api.js`

- Axios instance with **`baseURL: window.location.origin`**.
- Attaches **`Authorization: Bearer`** from `localStorage` for non-public `/api` calls.

#### `fronend/src/router/index.js`

- `/` → redirect `/login`
- `/login` → **`Loginview.vue`**
- `/chat` → **`Chatview.vue`**

#### `fronend/src/views/Loginview.vue`

- Login / register forms; stores **`access_token`** and **`username`** in `localStorage`; navigates to **`/chat`**.

#### `fronend/src/components/Sidebar.vue`

- Loads **group rooms**, **direct rooms**, **users** via API.
- Click channel → emit **`select-room`** (group may **`POST /api/rooms/join/`** first).
- Click user → **`POST /api/rooms/direct/`** then open that room.

#### `fronend/src/views/Chatview.vue` (largest piece)

- State: **`messages`**, **`roomId`**, **`currentUser`**, WebSocket **`socket`** + **`notifySocket`**.
- **`handleRoomSelect`**: set room, **`fetchMessages()`**, **`initWebSocket()`** to `ws/chat/<roomId>/`.
- **`fetchMessages`**: **`GET /api/messages/?room_id=`** — loads `seen_by`, `room_type`, etc.
- **`initWebSocket`**: on **`join`**, marks room read (direct); handles incoming **`message`**, **`delete`**, **`edit`**, **`status_update`**, **`read_receipt`**.
- **`sendMessage`**: prefers WS **`send`**; falls back to **`POST /api/messages/`** if socket down.
- Group-specific: **`setupGroupReadObserver`**, **`tryGroupMessageSeen`**, **`sendMarkMessageSeen`** for read receipts.

#### `fronend/vite.config.js`

- **`server.proxy`**: `/api` → `http://localhost:8000`, **`/ws`** → `ws://localhost:8000` so dev uses one origin.

### Mental model (one paragraph)

**Users and rooms** live in the **database** (`Room`, `Message`, `MessageRead`). **REST** handles auth, listing rooms/users, and loading/sometimes posting messages. **WebSockets** keep the **active chat** in sync: new messages, edits, deletes, delivery/viewed ticks for **direct** chats, and **`read_receipt`** updates for **group** “seen by”. **Notifications** socket exists mainly to upgrade **`sent` → `delivered`** when recipients are connected.

### Suggested reading order

1. `backend/chat/models.py`
2. `backend/backend/urls.py` + `backend/chat/views.py`
3. `backend/chat/consumers.py` (skim `receive` and the `async def *_` event handlers)
4. `backend/backend/asgi.py` + `backend/chat/routing.py`
5. `fronend/src/api.js` → `router/index.js` → `Sidebar.vue` → `Chatview.vue`

## 🔎 Troubleshooting

- **WebSocket doesn’t connect**
  - Ensure Django is running and `backend/backend/asgi.py` is used (Channels).
  - In dev, `fronend/vite.config.js` proxies `/ws` to `ws://localhost:8000`.

- **401 errors from `/api/*`**
  - Login stores `access_token` in `localStorage`.
  - Requests attach `Authorization: Bearer ...` in `fronend/src/api.js`.

- **Group room messages don’t show “Seen by …”**
  - Read receipts are stored in `MessageRead` and emitted as WS `read_receipt`.
  - Make sure multiple users joined the same group room via the sidebar (join endpoint).
