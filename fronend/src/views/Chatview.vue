<template>
  <div class="chat-container">
    <div class="chat-header">
      <h2>Room: {{ roomName }}</h2>
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
          <strong class="msg-user">{{ msg.username }}</strong> 
          <p class="msg-content">{{ msg.content }}</p>
          <small class="timestamp">{{ formatTime(msg.created_at) }}</small>
        </div>
      </div>
      <div v-if="messages.length === 0" class="no-messages">
        No messages yet. Start the conversation!
      </div>
    </div>

    <div class="input-area">
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
</template>

<script>
import api from '../api';

export default {
  data() {
    return {
      roomName: "General",
      messages: [],
      newMessage: "",
      currentUser: localStorage.getItem('username') || "Guest",
      pollingInterval: null,
      sending: false,
      roomId: this.$route.params.id || '1' // Default to room 1
    };
  },
  methods: {
    async fetchMessages() {
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
      if (!this.newMessage.trim() || this.sending) return;

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
      this.$router.push('/login');
    }
  },

  mounted() {
    // Check for auth
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login');
      return;
    }
    
    this.fetchMessages();
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
.chat-container {
  max-width: 800px;
  margin: 20px auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  height: 80vh;
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

.logout-btn:hover {
  background: rgba(255,255,255,0.3);
}

.message-display {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 1rem;
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
  padding: 0.8rem 1.2rem;
  border-radius: 18px;
  position: relative;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.sent .message-bubble {
  background: #dcf8c6;
  border-bottom-right-radius: 4px;
}

.received .message-bubble {
  background: white;
  border-bottom-left-radius: 4px;
}

.msg-user {
  display: block;
  font-size: 0.75rem;
  color: #666;
  margin-bottom: 0.2rem;
}

.msg-content {
  margin: 0;
  word-wrap: break-word;
}

.timestamp {
  display: block;
  font-size: 0.65rem;
  color: #999;
  text-align: right;
  margin-top: 0.3rem;
}

.no-messages {
  text-align: center;
  color: #999;
  margin-top: 2rem;
  font-style: italic;
}

.input-area {
  padding: 1.5rem 2rem;
  background: white;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
}

input {
  flex: 1;
  padding: 0.8rem 1.2rem;
  border: 2px solid #f0f0f0;
  border-radius: 25px;
  outline: none;
  transition: border-color 0.2s;
}

input:focus {
  border-color: #4CAF50;
}

button {
  padding: 0.8rem 1.5rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: bold;
  cursor: pointer;
  transition: opacity 0.2s;
}

button:hover:not(:disabled) {
  opacity: 0.9;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>