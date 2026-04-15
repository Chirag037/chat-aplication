<template>
  <div class="flex h-screen bg-white overflow-hidden font-sans text-slate-900 selection:bg-slate-200">
    <!-- Sidebar -->
    <Sidebar 
      :activeRoomId="roomId" 
      :isOpen="isSidebarOpen" 
      @select-room="handleRoomSelect" 
      @close="isSidebarOpen = false"
    />
    
    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col min-w-0 bg-white overflow-hidden">
      
      <!-- Minimalist Header -->
      <header class="h-14 flex items-center justify-between px-6 bg-white border-b border-slate-100 z-10 shrink-0">
        <div class="flex items-center gap-3">
          <button @click="isSidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-400 hover:bg-slate-50 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
          </button>
          <div>
            <h2 class="text-sm font-bold text-slate-900 tracking-tight">{{ currentRoomName }}</h2>
            <div v-if="roomId" class="flex items-center gap-1.5 py-0.5">
              <span class="w-1 h-1 bg-slate-200 rounded-full"></span>
              <span class="text-[9px] font-bold text-slate-400 uppercase tracking-[0.15em]">Direct Message</span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-6">
          <div class="hidden sm:flex items-center gap-3">
            <span class="text-[10px] font-bold text-slate-300 uppercase tracking-widest">{{ currentUser }}</span>
            <div class="w-7 h-7 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-center text-[10px] font-bold text-slate-400">
              {{ getInitial(currentUser) }}
            </div>
          </div>
          <button @click="logout" class="text-[10px] font-bold text-slate-400 hover:text-slate-900 uppercase tracking-widest transition-colors duration-200">
            Sign Out
          </button>
        </div>
      </header>

      <!-- Message Display -->
      <main class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 bg-slate-50 transition-colors duration-300" ref="messageWindow">
        <div 
          v-for="(msg, index) in messages" 
          :key="msg.id || index" 
          :class="['flex flex-col w-full', msg.username === currentUser ? 'items-end' : 'items-start']"
        >
          <!-- Metadata -->
          <div class="flex items-center gap-2 mb-1 px-1 opacity-60">
             <span v-if="msg.username !== currentUser" class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              {{ msg.username }}
            </span>
            <span class="text-[9px] font-medium text-slate-300 uppercase letter-spacing-wide">
              {{ formatTime(msg.created_at) }}
            </span>
          </div>

          <!-- Bubble Container -->
          <div class="group relative flex items-center">
            <!-- Edit/Delete Actions (Left side for sent messages) -->
            <div v-if="msg.username === currentUser && editingMessageId !== msg.id" class="hidden group-hover:flex items-center gap-1 mr-2 bg-white/10 backdrop-blur-md border border-white/10 rounded-lg p-1 transition-all duration-200">
              <button @click="startEdit(msg)" class="p-1 hover:bg-white/20 rounded transition-colors" title="Edit message">
                <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
              </button>
              <button @click="deleteMessage(msg.id)" class="p-1 hover:bg-red-500/20 rounded transition-colors" title="Delete message">
                <svg class="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>

            <!-- Bubble Content -->
            <div 
              :class="[
                'px-5 py-3 shadow-sm transition-all duration-300 text-sm leading-relaxed min-w-[60px]',
                msg.username === currentUser 
                  ? 'bg-green-100 text-green-900 rounded-xl rounded-tr-none border border-green-200' 
                  : 'bg-blue-100 text-blue-900 rounded-xl rounded-tl-none border border-blue-200'
              ]"
            >
              <!-- Normal View -->
              <div v-if="editingMessageId !== msg.id">
                <p class="whitespace-pre-wrap">{{ msg.content }}</p>
                <div class="mt-1.5 flex items-center justify-end gap-1.5 px-0.5">
                  <span class="text-[9px] font-medium opacity-60 uppercase tracking-tighter">
                    {{ formatTime(msg.created_at) }}
                  </span>
                  <span v-if="msg.is_edited" class="text-[8px] italic opacity-40">Edited</span>
                </div>
              </div>

              <!-- Inline Edit View -->
              <div v-else class="flex flex-col gap-2 min-w-[200px]">
                <textarea 
                  v-model="editingContent" 
                  class="w-full bg-white/50 border border-green-300 rounded-lg p-2 text-sm text-green-900 outline-none focus:ring-2 focus:ring-green-400 resize-none"
                  rows="2"
                  @keyup.esc="cancelEdit"
                  @keyup.enter.exact.prevent="saveEdit"
                ></textarea>
                <div class="flex justify-end gap-2">
                  <button @click="cancelEdit" class="text-[10px] font-bold text-slate-500 uppercase tracking-widest hover:text-slate-700">Cancel</button>
                  <button @click="saveEdit" class="text-[10px] font-bold text-green-600 uppercase tracking-widest hover:text-green-800">Save</button>
                </div>
              </div>
            </div>

            <!-- Status Icons & Seen By -->
            <div v-if="msg.username === currentUser" class="absolute -bottom-5 right-1 flex items-center gap-2 h-4">
              <!-- Seen By (Group rooms only) - Shown to the left of the icon -->
              <span v-if="msg.seen_by && msg.seen_by.length > 0" class="text-[8px] text-blue-500 font-bold whitespace-nowrap">
                Seen by {{ msg.seen_by.join(', ') }}
              </span>

              <!-- Viewed (Blue Circle) -->
              <div v-if="msg.status === 'viewed' || (msg.seen_by && msg.seen_by.length > 0)" class="w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_6px_rgba(59,130,246,0.6)] border border-blue-400"></div>
              
              <!-- Delivered (Double Tick) -->
              <div v-else-if="msg.status === 'delivered'" class="flex -space-x-1.5 opacity-60">
                <svg class="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                <svg class="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
              </div>
              
              <!-- Sent (Single Tick) -->
              <div v-else class="opacity-30">
                <svg class="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty States -->
        <div v-if="!roomId" class="h-full flex flex-col items-center justify-center text-center px-4 max-w-sm mx-auto">
          <div class="w-12 h-12 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center mb-6">
            <svg class="w-6 h-6 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
          </div>
          <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wider">No Active Session</h3>
          <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">Select a destination from the sidebar to begin your communication session.</p>
        </div>
        
        <div v-else-if="messages.length === 0" class="h-full flex items-center justify-center">
          <p class="text-[10px] font-bold text-slate-300 uppercase tracking-[0.3em] italic">Session Initialized</p>
        </div>
      </main>

      <!-- Minimalist Input Bar -->
      <footer class="p-6 md:p-8 bg-white shrink-0 shadow-[0_-1px_0_0_rgba(241,245,249,1)]">
        <div class="w-full flex items-center gap-4">
          <div class="flex-1 flex items-center bg-slate-50 border border-slate-100 rounded-xl focus-within:bg-white focus-within:border-slate-900 focus-within:shadow-lg focus-within:shadow-slate-200/20 transition-all duration-200 overflow-hidden">
            <input 
              v-model="newMessage" 
              @keyup.enter="sendMessage" 
              placeholder="Start typing..." 
              type="text"
              :disabled="sending"
              class="flex-1 bg-transparent px-5 py-3.5 text-sm placeholder-slate-300 outline-none disabled:opacity-50"
            />
            <button 
              @click="sendMessage" 
              :disabled="!newMessage.trim() || sending"
              class="px-5 group disabled:opacity-30"
            >
              <svg v-if="!sending" class="w-5 h-5 text-slate-400 group-hover:text-slate-900 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
              <svg v-else class="animate-spin h-4 w-4 text-slate-400" viewBox="0 0 24 24">
                <circle class="opacity-10" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-40" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </button>
          </div>
        </div>
      </footer>
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
      sending: false,
      roomId: localStorage.getItem('last_room_id') || null,
      currentRoomName: "Select Workspace",
      isSidebarOpen: false,
      socket: null,
      notifySocket: null,
      editingMessageId: null,
      editingContent: ""
    };
  },
  methods: {
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : '?';
    },
    async handleRoomSelect(payload) {
      const room = typeof payload === 'object' ? payload : null;
      const id = room ? room.id : payload;
      
      this.roomId = id;
      localStorage.setItem('last_room_id', id);
      this.isSidebarOpen = false;
      this.fetchMessages();
      this.initWebSocket();
      
      if (room) {
        if (room.type === 'direct') {
          const other = room.participants.find(p => p.username !== this.currentUser);
          this.currentRoomName = other ? other.username : 'Private Session';
        } else {
          this.currentRoomName = room.name || `Session ${room.id}`;
        }
      } else {
        // Fallback if just an ID is somehow passed
        try {
          const [groupRes, directRes] = await Promise.all([
            api.get('/api/rooms/group/'),
            api.get('/api/rooms/')
          ]);
          const allRooms = [...groupRes.data, ...directRes.data];
          const foundRoom = allRooms.find(r => r.id == id);
          if (foundRoom) {
            if (foundRoom.type === 'direct') {
              const other = foundRoom.participants.find(p => p.username !== this.currentUser);
              this.currentRoomName = other ? other.username : 'Private Session';
            } else {
              this.currentRoomName = foundRoom.name || `Session ${foundRoom.id}`;
            }
          }
        } catch (e) {
          console.error('Context error:', e);
        }
      }
    },
    initWebSocket() {
      if (this.socket) {
        this.socket.close();
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const socketUrl = `${protocol}//${window.location.host}/ws/chat/${this.roomId}/`;
      
      this.socket = new WebSocket(socketUrl);

      this.socket.onopen = () => {
         this.socket.send(JSON.stringify({
            'action': 'join',
            'username': this.currentUser
         }));
         this.markRoomAsRead();
      };

      this.socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data && data.room == this.roomId) {
          if (data.type === 'message' ) {
             this.messages.push({
               username: data.username,
               content: data.content,
               created_at: data.created_at,
               id: data.id || Date.now(),
               status: data.status || 'sent',
               room_type: data.room_type,
               seen_by: [],
             });
             this.$nextTick(this.scrollToBottom);
          } else if (data.type === 'delete') {
             this.messages = this.messages.filter(m => m.id !== data.message_id);
          } else if (data.type === 'edit') {
             const msg = this.messages.find(m => m.id === data.message_id);
             if (msg) {
               msg.content = data.content;
               msg.is_edited = true;
             }
          } else if (data.type === 'status_update') {
             // If the OTHER person updated their view/delivery status, update my sent messages
             if (data.username !== this.currentUser) {
               this.messages.forEach(m => {
                 if (m.username === this.currentUser) {
                    // Never downgrade: viewed > delivered > sent
                    if (data.status === 'viewed' && m.status !== 'viewed') {
                      m.status = 'viewed';
                    } 
                    else if (data.status === 'delivered' && m.status === 'sent') {
                      m.status = 'delivered';
                    }
                 }
               });
             }
           } else if (data.type === 'read_receipt') {
             // Group room: update the specific message's seen_by list
             const msg = this.messages.find(m => m.id === data.message_id);
             if (msg) {
               msg.seen_by = data.seen_by || [];
               // If this is the sender's own message and someone else saw it, mark as viewed
               if (msg.username === this.currentUser && msg.seen_by.length > 0) {
                 msg.status = 'viewed';
               }
             }
           }
        }
        
        // If we get a new message while in this room, mark it as read
        if (data.type === 'message' && data.username !== this.currentUser) {
          this.markRoomAsRead();
        }
      };

      this.socket.onclose = (e) => {
        console.log('Socket closed');
      };
    },

    initNotificationSocket() {
      if (this.notifySocket) return;

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const socketUrl = `${protocol}//${window.location.host}/ws/notifications/`;
      
      this.notifySocket = new WebSocket(socketUrl);

      this.notifySocket.onopen = () => {
         this.notifySocket.send(JSON.stringify({
            'action': 'join',
            'username': this.currentUser
         }));
      };

      this.notifySocket.onclose = () => {
        this.notifySocket = null;
        setTimeout(this.initNotificationSocket, 3000);
      };
    },
    async fetchMessages() {
      if (!this.roomId) return;
      try {
        const response = await api.get(`/api/messages/?room_id=${this.roomId}`);
        this.messages = response.data;
        this.$nextTick(this.scrollToBottom);
      } catch (error) {
        console.error("Communication error:", error);
        if (error.response?.status === 401) {
          this.$router.push('/login');
        }
      }
    },

    async sendMessage() {
      if (!this.newMessage.trim() || this.sending || !this.roomId) return;

      this.sending = true;
      try {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          this.socket.send(JSON.stringify({
            'action': 'send',
            'message': this.newMessage,
            'username': this.currentUser
          }));
          
          this.newMessage = "";
          this.$nextTick(this.scrollToBottom);
        } else {
          const payload = { room: this.roomId, content: this.newMessage };
          await api.post('/api/messages/', payload);
          this.newMessage = ""; 
          await this.fetchMessages();
        }
      } catch (error) {
        console.error("Link error:", error);
      } finally {
        this.sending = false;
      }
    },

    deleteMessage(id) {
      if (!confirm("Are you sure you want to delete this message?")) return;
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          'action': 'delete',
          'message_id': id,
          'username': this.currentUser
        }));
        // Remove locally immediately for better UX
        this.messages = this.messages.filter(m => m.id !== id);
      }
    },

    startEdit(msg) {
      this.editingMessageId = msg.id;
      this.editingContent = msg.content;
    },

    cancelEdit() {
      this.editingMessageId = null;
      this.editingContent = "";
    },

    async saveEdit() {
      if (!this.editingContent.trim()) return;
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          'action': 'edit',
          'message_id': this.editingMessageId,
          'message': this.editingContent,
          'username': this.currentUser
        }));

        // Update locally
        const msg = this.messages.find(m => m.id === this.editingMessageId);
        if (msg) {
          msg.content = this.editingContent;
          msg.is_edited = true;
        }
        
        this.cancelEdit();
      }
    },

    markRoomAsRead() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN && this.roomId) {
        this.socket.send(JSON.stringify({
          'action': 'mark_read',
          'username': this.currentUser
        }));
      }
    },

    scrollToBottom() {
      const el = this.$refs.messageWindow;
      if (el) el.scrollTop = el.scrollHeight;
    },

    formatTime(timestamp) {
      if (!timestamp) return '';
      return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
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

    this.initNotificationSocket();

    if (this.roomId) {
      await this.fetchMessages();
      this.initWebSocket();
    }
  },

  beforeUnmount() {
    if (this.socket) this.socket.close();
  }
};
</script>

<style scoped>
/* Redundant scoped styles removed - All migrated to Tailwind utility classes */
</style>
