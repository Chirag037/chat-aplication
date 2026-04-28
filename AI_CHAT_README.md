# AI Chat README

## Overview
The AI chat now supports persistent, database-backed conversation memory per user.

- Messages are stored in Django models.
- AI responses can use prior messages from the same conversation as context.
- A **New Chat** button creates a fresh conversation with no previous context.

## Backend Data Model
Two new models are used:

- `AIConversation`
  - `user` (owner)
  - `title`
  - `created_at`
  - `updated_at`
- `AIMessage`
  - `conversation` (FK to `AIConversation`)
  - `role` (`user` or `assistant`)
  - `content`
  - `created_at`

## API Endpoints

- `GET /api/ai/conversation/`
  - Loads (or creates) the default AI conversation for the authenticated user.
  - Returns conversation metadata + messages.

- `POST /api/ai/conversation/new/`
  - Creates a brand-new AI conversation for the authenticated user.
  - Use this to start with zero prior context.

- `POST /api/ai/chat/`
  - Sends prompt to AI and stores both user + assistant messages.
  - Supports `conversation_id` to target a specific conversation.
  - AI context is built from recent messages in that conversation only.

## Frontend Behavior (AIChatView)

- On mount, the app loads saved conversation history from `/api/ai/conversation/`.
- Sending a message calls `/api/ai/chat/` with the active `conversation_id`.
- Clicking **New Chat**:
  1. calls `/api/ai/conversation/new/`
  2. switches UI to that new conversation
  3. ensures no context from older conversations is used

## Setup Notes

Run migrations after pulling changes:

```bash
cd backend
python manage.py migrate
```

Then run your normal backend + frontend startup commands.
