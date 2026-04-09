<template>
  <div class="main-layout">
    <Sidebar :activeRoomId="roomId" @select-room="handleRoomSelect" />
    
    <div class="chat-container">
      <div class="chat-header">
        <h2>{{ currentRoomName }}</h2>
        <div class="user-info">
          <span>Logged in as: <strong>{{ currentUser }}</strong></span>
          <button @click="logout" class="logout-btn">Logout</button>
        </div>
      </div>

      <div class="message-display" ref="messageWindow">
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
          :class="['message-item', msg.username === currentUser ? 'sent' : 'received']"
        >
          <div class="message-bubble">
            <strong class="msg-user" v-if="msg.username !== currentUser">{{ msg.username }}</strong> 
            <p class="msg-content">{{ msg.content }}</p>
            <small class="timestamp">{{ formatTime(msg.created_at) }}</small>
          </div>
        </div>
        <div v-if="!roomId" class="no-messages">
          Select a conversation to start chatting!
        </div>
        <div v-else-if="messages.length === 0" class="no-messages">
          No messages yet. Start the conversation!
        </div>
      </div>

      <div class="input-area" v-if="roomId">
        <input 
          v-model="newMessage" 
          @keyup.enter="sendMessage" 
          placeholder="Type a message..." 
          type="text"
          :disabled="sending"
        />
        <button @click="sendMessage" :disabled="!newMessage.trim() || sending">
          {{ sending ? 'Sending...' : 'Send' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';
import Sidebar from '../components/Sidebar.vue';

export default {
  components: { Sidebar },
  data() {
    return {
      messages: [],
      newMessage: "",
      currentUser: localStorage.getItem('username') || "Guest",
      pollingInterval: null,
      sending: false,
      roomId: localStorage.getItem('last_room_id') || null,
      currentRoomName: "Select a Chat"
    };
  },
  methods: {
    async handleRoomSelect(id) {
      this.roomId = id;
      localStorage.setItem('last_room_id', id);
      this.fetchMessages();

      // Fetch room name from both group and direct rooms
      try {
        const [groupRes, directRes] = await Promise.all([
          api.get('/api/rooms/group/'),
          api.get('/api/rooms/')
        ]);
        const allRooms = [...groupRes.data, ...directRes.data];
        const room = allRooms.find(r => r.id == id);
        if (room) {
          if (room.type === 'direct') {
            const other = room.participants.find(p => p.username !== this.currentUser);
            this.currentRoomName = other ? `@ ${other.username}` : 'Direct Chat';
          } else {
            this.currentRoomName = `# ${room.name || `Room ${room.id}`}`;
          }
        }
      } catch (e) {
        console.error('Error updating room name:', e);
      }
    },
    async fetchMessages() {
      if (!this.roomId) return;
      try {
        const response = await api.get(`/api/messages/?room_id=${this.roomId}`);
        this.messages = response.data;
        
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      } catch (error) {
        console.error("Error fetching messages:", error);
        if (error.response?.status === 401) {
          this.$router.push('/login');
        }
      }
    },

    async sendMessage() {
      if (!this.newMessage.trim() || this.sending || !this.roomId) return;

      this.sending = true;
      const payload = {
        room: this.roomId,
        content: this.newMessage
      };

      try {
        await api.post('/api/messages/', payload);
        this.newMessage = ""; 
        await this.fetchMessages(); 
      } catch (error) {
        console.error("Error sending message:", error);
        alert("Failed to send message. Please check your connection.");
      } finally {
        this.sending = false;
      }
    },

    scrollToBottom() {
      const el = this.$refs.messageWindow;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    },

    formatTime(timestamp) {
      if (!timestamp) return '';
      return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },

    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('username');
      localStorage.removeItem('last_room_id');
      this.$router.push('/login');
    }
  },

  async mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login');
      return;
    }

    if (this.roomId) {
      this.fetchMessages();
    }
    this.pollingInterval = setInterval(this.fetchMessages, 3000);
  },

  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  }
};
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
  margin: 10px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.05);
  overflow: hidden;
}

.chat-header {
  padding: 1rem 2rem;
  background: #4CAF50;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
}

.logout-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid white;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.message-display {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.message-item {
  display: flex;
  width: 100%;
}

.sent {
  justify-content: flex-end;
}

.received {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 0.6rem 1rem;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

.sent .message-bubble {
  background: #dcf8c6;
  border-bottom-right-radius: 2px;
}

.received .message-bubble {
  background: white;
  border-bottom-left-radius: 2px;
}

.msg-user {
  display: block;
  font-size: 0.7rem;
  color: #666;
  margin-bottom: 0.2rem;
}

.msg-content {
  margin: 0;
  word-wrap: break-word;
  font-size: 0.95rem;
}

.timestamp {
  display: block;
  font-size: 0.6rem;
  color: #999;
  text-align: right;
  margin-top: 0.2rem;
}

.no-messages {
  text-align: center;
  color: #999;
  margin-top: 4rem;
  font-style: italic;
}

.input-area {
  padding: 1rem 2rem;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
}

input {
  flex: 1;
  padding: 0.7rem 1.2rem;
  border: 1px solid #ddd;
  border-radius: 25px;
  outline: none;
}

input:focus {
  border-color: #4CAF50;
}

button {
  padding: 0.7rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>