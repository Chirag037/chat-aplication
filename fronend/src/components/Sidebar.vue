<template>
  <div :class="['fixed inset-0 z-50 transition-all duration-300 md:relative md:flex md:w-64 md:translate-x-0', isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0']">
    <!-- Mobile Backdrop -->
    <div 
      v-if="isOpen" 
      @click="$emit('close')" 
      class="absolute inset-0 bg-black/40 backdrop-blur-sm md:hidden"
    ></div>

    <!-- Sidebar Content -->
    <div class="relative w-60 md:w-full h-full bg-slate-900 border-r border-slate-800 flex flex-col overflow-y-auto">
      
      <!-- Brand/Header -->
      <div class="px-6 py-6 flex items-center gap-3">
        <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center shadow-lg">
          <span class="text-slate-900 font-black text-sm">C</span>
        </div>
        <h1 class="text-white font-bold text-sm tracking-[0.2em] uppercase">Workspace</h1>
      </div>

      <!-- Rooms Section -->
      <div class="px-3 mb-6">
        <h3 class="px-4 mb-3 text-[9px] font-bold text-slate-500 uppercase tracking-[0.25em]">Channels</h3>
        <div v-if="groupRooms.length === 0" class="px-4 py-2 text-[10px] text-slate-600 uppercase tracking-wider italic">None</div>
        <div
          v-for="room in groupRooms"
          :key="'g-' + room.id"
          :class="[
            'group flex items-center px-4 py-2 rounded-lg cursor-pointer transition-all duration-200 mb-0.5',
            activeRoomId == room.id ? 'bg-slate-800 text-white font-bold' : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-200'
          ]"
          @click="selectGroupRoom(room)"
        >
          <span :class="['w-4 text-[10px] font-bold mr-2 transition-colors', activeRoomId == room.id ? 'text-white' : 'text-slate-700 group-hover:text-slate-500']">#</span>
          <span class="truncate text-[11px] uppercase tracking-wider">{{ room.name || `Session ${room.id}` }}</span>
        </div>
      </div>

      <!-- Direct Messages Section -->
      <div class="px-3 mb-6">
        <h3 class="px-4 mb-3 text-[9px] font-bold text-slate-500 uppercase tracking-[0.25em]">Direct</h3>
        <div v-if="directRooms.length === 0" class="px-4 py-2 text-[10px] text-slate-600 uppercase tracking-wider italic">None</div>
        <div
          v-for="room in directRooms"
          :key="'d-' + room.id"
          :class="[
            'group flex items-center px-4 py-2 rounded-lg cursor-pointer transition-all duration-200 mb-0.5',
            activeRoomId == room.id ? 'bg-slate-800 text-white font-bold' : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-200'
          ]"
          @click="selectRoom(room.id)"
        >
          <div :class="['w-4 h-4 rounded-md flex items-center justify-center text-[8px] mr-3 font-black transition-colors', activeRoomId == room.id ? 'bg-white text-slate-900' : 'bg-slate-800 text-slate-500 group-hover:bg-slate-700']">
            {{ getInitial(getRoomName(room)) }}
          </div>
          <span class="truncate text-[11px] uppercase tracking-wider">{{ getRoomName(room) }}</span>
        </div>
      </div>

      <!-- People Section -->
      <div class="px-3 mb-8">
        <h3 class="px-4 mb-3 text-[9px] font-bold text-slate-500 uppercase tracking-[0.25em]">Teammates</h3>
        <div v-if="users.length === 0" class="px-4 py-2 text-[10px] text-slate-600 uppercase tracking-wider italic">None</div>
        <div
          v-for="user in users"
          :key="'u-' + user.id"
          class="group flex items-center px-4 py-2 rounded-lg cursor-pointer text-slate-500 hover:bg-slate-800/50 hover:text-slate-200 transition-all duration-200 mb-0.5"
          @click="startDirectChat(user.id)"
        >
          <div class="w-4 h-4 rounded-md bg-slate-800 flex items-center justify-center text-[8px] mr-3 font-black text-slate-500 group-hover:bg-slate-700 transition-colors">
            {{ getInitial(user.username) }}
          </div>
          <span class="truncate text-[11px] uppercase tracking-wider">{{ user.username }}</span>
        </div>
      </div>

      <!-- Current User Info -->
      <div class="mt-auto p-4 bg-black/20">
        <div class="flex items-center gap-3 px-2">
          <div class="w-7 h-7 rounded-lg bg-white flex items-center justify-center text-slate-900 text-[10px] font-black">
            {{ getInitial(currentUser) }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[10px] font-black text-white uppercase tracking-widest truncate">{{ currentUser }}</p>
            <div class="flex items-center gap-1.5 mt-0.5">
              <span class="w-1 h-1 bg-slate-500 rounded-full"></span>
              <span class="text-[8px] font-bold text-slate-500 uppercase tracking-tighter">Authorized</span>
            </div>
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
      } catch (error) {
        console.error('Context error:', error);
      }
    },
    getRoomName(room) {
      if (room.type === 'direct') {
        const other = room.participants.find(p => p.username !== this.currentUser);
        return other ? other.username : 'Session';
      }
      return room.name || `Session ${room.id}`;
    },
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : '?';
    },
    selectRoom(roomId) {
      this.$emit('select-room', roomId);
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
      this.$emit('select-room', room.id);
    },
    async startDirectChat(userId) {
      try {
        const response = await api.post('/api/rooms/direct/', { user_id: userId });
        const room = response.data;
        this.$emit('select-room', room.id);
        this.fetchData();
      } catch (error) {
        console.error('Session error:', error);
      }
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
