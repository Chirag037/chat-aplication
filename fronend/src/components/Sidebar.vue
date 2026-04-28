<template>
  <div :class="['fixed inset-0 z-50 transition-all duration-300 md:relative md:flex md:w-64 md:translate-x-0', isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0']">
    <!-- Mobile Backdrop -->
    <div 
      v-if="isOpen" 
      @click="$emit('close')" 
      class="absolute inset-0 bg-black/40 backdrop-blur-sm md:hidden"
    ></div>

    <!-- Sidebar Content -->
    <div class="relative w-60 md:w-full h-full bg-gradient-to-b from-[#fff7ed] via-[#fff1e6] to-[#ffedd5] border-r border-amber-200/80 flex flex-col overflow-y-auto">
      
      <!-- Brand/Header -->
      <div class="px-5 py-5 flex items-center gap-3 border-b border-amber-200">
        <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-sm ring-1 ring-amber-200/60">
          <span class="text-amber-950 font-extrabold text-sm">C</span>
        </div>
        <div class="min-w-0">
          <h1 class="text-slate-900 font-semibold text-sm tracking-tight truncate">Workspace</h1>
          <p class="text-amber-900/50 text-xs truncate">Chat</p>
        </div>
      </div>

      <!-- Rooms Section -->
      <div class="px-3 mb-6">
        <h3 class="px-4 mb-2 text-[11px] font-semibold text-amber-900/60 uppercase tracking-wider">Channels</h3>
        <div v-if="groupRooms.length === 0" class="px-4 py-2 text-xs text-slate-500 italic">No channels</div>
        <div
          v-for="room in groupRooms"
          :key="'g-' + room.id"
          :class="[
            'group relative flex items-center px-4 py-2 rounded-md cursor-pointer select-none transition-all duration-200 mb-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/40 active:scale-[0.99]',
            activeRoomId == room.id ? 'bg-white text-slate-900 font-semibold shadow-sm ring-1 ring-amber-300/70' : 'text-slate-700 hover:bg-amber-100/60 hover:text-slate-900'
          ]"
          @click="selectGroupRoom(room)"
        >
          <span v-if="activeRoomId == room.id" class="absolute left-1 top-1/2 -translate-y-1/2 h-5 w-1 rounded-full bg-gradient-to-b from-amber-500 to-rose-500"></span>
          <span :class="['w-4 text-sm font-semibold mr-2 transition-colors', activeRoomId == room.id ? 'text-amber-700' : 'text-amber-700/45 group-hover:text-amber-700/70']">#</span>
          <span class="truncate text-[13px] font-medium tracking-tight">{{ room.name || `Session ${room.id}` }}</span>
        </div>
      </div>

      <!-- Direct Messages Section -->
      <div class="px-3 mb-6">
        <h3 class="px-4 mb-2 text-[11px] font-semibold text-amber-900/60 uppercase tracking-wider">Direct messages</h3>
        <div v-if="directRooms.length === 0" class="px-4 py-2 text-xs text-slate-500 italic">No conversations</div>
        <div
          v-for="room in directRooms"
          :key="'d-' + room.id"
          :class="[
            'group relative flex items-center px-4 py-2 rounded-md cursor-pointer select-none transition-all duration-200 mb-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/40 active:scale-[0.99]',
            activeRoomId == room.id ? 'bg-white text-slate-900 font-semibold shadow-sm ring-1 ring-amber-300/70' : 'text-slate-700 hover:bg-amber-100/60 hover:text-slate-900'
          ]"
          @click="selectRoom(room)"
        >
          <span v-if="activeRoomId == room.id" class="absolute left-1 top-1/2 -translate-y-1/2 h-5 w-1 rounded-full bg-gradient-to-b from-amber-500 to-rose-500"></span>
          <div :class="['w-7 h-7 rounded-md flex items-center justify-center text-xs mr-3 font-semibold transition-colors ring-1', activeRoomId == room.id ? 'bg-amber-50 text-amber-950 ring-amber-200' : 'bg-white/60 text-amber-900 ring-amber-200/60 group-hover:bg-white']">
            {{ getInitial(getRoomName(room)) }}
          </div>
          <span class="truncate text-[13px] font-medium tracking-tight">{{ getRoomName(room) }}</span>
        </div>
      </div>

      <!-- People Section -->
      <div class="px-3 mb-8">
        <h3 class="px-4 mb-2 text-[11px] font-semibold text-amber-900/60 uppercase tracking-wider">People</h3>
        <div v-if="users.length === 0" class="px-4 py-2 text-xs text-slate-500 italic">No users</div>
        <div
          v-for="user in users"
          :key="'u-' + user.id"
          class="group flex items-center px-4 py-2 rounded-md cursor-pointer select-none text-slate-700 hover:bg-amber-100/60 hover:text-slate-900 transition-all duration-200 mb-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/40 active:scale-[0.99]"
          @click="startDirectChat(user.id)"
        >
          <div class="w-7 h-7 rounded-md bg-white/60 ring-1 ring-amber-200/60 flex items-center justify-center text-xs mr-3 font-semibold text-amber-900 group-hover:bg-white transition-colors">
            {{ getInitial(user.username) }}
          </div>
          <span class="truncate text-[13px] font-medium tracking-tight">{{ user.username }}</span>
        </div>
      </div>

      <!-- AI Section -->
      <div class="px-3 mb-6">
        <h3 class="px-4 mb-2 text-[11px] font-semibold text-amber-900/60 uppercase tracking-wider">AI</h3>
        <div
          class="group relative flex items-center px-4 py-2 rounded-md cursor-pointer select-none transition-all duration-200 mb-0.5 focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400/40 active:scale-[0.99] text-slate-700 hover:bg-amber-100/60 hover:text-slate-900"
          @click="goToAI"
        >
          <span class="w-7 h-7 rounded-md bg-white/60 ring-1 ring-amber-200/60 flex items-center justify-center text-xs mr-3 font-semibold text-amber-900 group-hover:bg-white transition-colors">
            AI
          </span>
          <span class="truncate text-[13px] font-medium tracking-tight">AI Chat</span>
        </div>
      </div>

      <!-- Current User Info -->
      <div class="mt-auto p-4 bg-gradient-to-b from-transparent to-amber-50/80 border-t border-amber-200/80">
        <div class="rounded-lg border border-amber-200/80 bg-white/80 px-3 py-3 shadow-sm">
          <div class="flex items-center justify-center gap-3">
            <div class="w-9 h-9 rounded-md bg-amber-50 flex items-center justify-center text-amber-950 text-sm font-semibold ring-1 ring-amber-200/60">
            {{ getInitial(currentUser) }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-slate-900 truncate">{{ currentUser }}</p>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="w-1.5 h-1.5 bg-amber-500 rounded-full"></span>
                <span class="text-xs font-medium text-amber-900/60">Online</span>
              </div>
            </div>
            <div class="w-2 h-2 rounded-full bg-amber-500/20 ring-1 ring-amber-500/20"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  props: ['activeRoomId', 'isOpen'],
  data() {
    return {
      groupRooms: [],
      directRooms: [],
      users: [],
      currentUser: localStorage.getItem('username'),
      consecutiveFetchFailures: 0,
    };
  },
  methods: {
    async fetchData() {
      try {
        const [groupRes, directRes, usersRes] = await Promise.all([
          api.get('/api/rooms/group/'),
          api.get('/api/rooms/'),
          api.get('/api/users/')
        ]);
        this.groupRooms = groupRes.data;
        this.directRooms = directRes.data;
        this.users = usersRes.data;
        this.consecutiveFetchFailures = 0;
      } catch (error) {
        console.error('Context error:', error);
        this.consecutiveFetchFailures += 1;

        // If backend/proxy is down (502/503/504) stop hammering; retry later.
        const status = error?.response?.status;
        if (status && status >= 500 && this.consecutiveFetchFailures >= 3) {
          clearInterval(this.interval);
          this.interval = null;
          setTimeout(() => {
            this.consecutiveFetchFailures = 0;
            this.fetchData();
            this.interval = setInterval(this.fetchData, 5000);
          }, 10000);
        }
      }
    },
    getRoomName(room) {
      if (room.type === 'direct') {
        const participants = Array.isArray(room.participants) ? room.participants : [];
        const other = participants.find(p => p.username !== this.currentUser);
        return other ? other.username : 'Session';
      }
      return room.name || `Session ${room.id}`;
    },
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : '?';
    },
    selectRoom(room) {
      this.$emit('select-room', room);
    },
    async selectGroupRoom(room) {
      const isMember = room.participants && room.participants.some(p => p.username === this.currentUser);
      if (!isMember) {
        try {
          await api.post('/api/rooms/join/', { room_id: room.id });
          await this.fetchData();
        } catch (error) {
          console.error('Auth error:', error);
        }
      }
      this.$emit('select-room', room);
    },
    async startDirectChat(userId) {
      try {
        const response = await api.post('/api/rooms/direct/', { user_id: userId });
        const room = response.data;
        this.$emit('select-room', room);
        this.fetchData();
      } catch (error) {
        console.error('Session error:', error);
      }
    },
    goToAI() {
      // Sidebar is used both in Chatview and AI view; routing is safe in both.
      this.$router.push('/ai');
    }
  },
  mounted() {
    this.fetchData();
    this.interval = setInterval(this.fetchData, 5000);
  },
  beforeUnmount() {
    clearInterval(this.interval);
  }
};
</script>

<style scoped>
/* Redundant scoped styles removed - All migrated to Tailwind utility classes */
</style>
