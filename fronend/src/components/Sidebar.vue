<template>
  <div class="sidebar">
    <!-- Rooms Section -->
    <div class="section">
      <h3><span class="section-icon">🏠</span> Rooms</h3>
      <div v-if="groupRooms.length === 0" class="empty">No rooms available</div>
      <div
        v-for="room in groupRooms"
        :key="'g-' + room.id"
        :class="['room-item', activeRoomId == room.id ? 'active' : '']"
        @click="selectGroupRoom(room)"
      >
        <span class="room-icon">#</span>
        <span class="room-name">{{ room.name || `Room ${room.id}` }}</span>
      </div>
    </div>

    <div class="divider"></div>

    <!-- Direct Messages Section -->
    <div class="section">
      <h3><span class="section-icon">💬</span> Direct Messages</h3>
      <div v-if="directRooms.length === 0" class="empty">No conversations yet</div>
      <div
        v-for="room in directRooms"
        :key="'d-' + room.id"
        :class="['room-item', activeRoomId == room.id ? 'active' : '']"
        @click="selectRoom(room.id)"
      >
        <span class="room-icon avatar">{{ getInitial(getRoomName(room)) }}</span>
        <span class="room-name">{{ getRoomName(room) }}</span>
      </div>
    </div>

    <div class="divider"></div>

    <!-- People Section -->
    <div class="section">
      <h3><span class="section-icon">👥</span> People</h3>
      <div v-if="users.length === 0" class="empty">No other users</div>
      <div
        v-for="user in users"
        :key="'u-' + user.id"
        class="user-item"
        @click="startDirectChat(user.id)"
      >
        <span class="room-icon avatar people-avatar">{{ getInitial(user.username) }}</span>
        <span class="user-name">{{ user.username }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api';

export default {
  props: ['activeRoomId'],
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
        console.error('Error fetching sidebar data:', error);
      }
    },
    getRoomName(room) {
      if (room.type === 'direct') {
        const other = room.participants.find(p => p.username !== this.currentUser);
        return other ? other.username : 'Direct Chat';
      }
      return room.name || `Room ${room.id}`;
    },
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : '?';
    },
    selectRoom(roomId) {
      this.$emit('select-room', roomId);
    },
    async selectGroupRoom(room) {
      // Auto-join the group room if not already a participant
      const isMember = room.participants && room.participants.some(p => p.username === this.currentUser);
      if (!isMember) {
        try {
          await api.post('/api/rooms/join/', { room_id: room.id });
          await this.fetchData();
        } catch (error) {
          console.error('Error joining room:', error);
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
        console.error('Error starting direct chat:', error);
        alert('Could not start chat');
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
.sidebar {
  width: 260px;
  background: #1e1f2e;
  border-right: 1px solid #2e2f45;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  color: #c9cdd4;
}

.section {
  padding: 0.75rem 0;
}

h3 {
  padding: 0.4rem 1rem;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6e7480;
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.section-icon {
  font-size: 0.85rem;
}

.divider {
  height: 1px;
  background: #2e2f45;
  margin: 0 1rem;
}

.room-item,
.user-item {
  padding: 0.55rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.7rem;
  cursor: pointer;
  border-radius: 6px;
  margin: 0 0.5rem;
  transition: background 0.15s;
  font-size: 0.9rem;
}

.room-item:hover,
.user-item:hover {
  background: #2a2b3d;
  color: #fff;
}

.room-item.active {
  background: #3b3d57;
  color: #7c8cff;
  font-weight: 600;
}

.room-icon {
  font-size: 1rem;
  font-weight: 700;
  color: #6e7480;
  min-width: 22px;
  text-align: center;
}

.room-item.active .room-icon {
  color: #7c8cff;
}

.avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #3b3d57;
  color: #a0a8ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}

.people-avatar {
  background: #2d3a2d;
  color: #6fcf97;
}

.room-name,
.user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty {
  padding: 0.35rem 1rem;
  font-size: 0.8rem;
  color: #4a4f61;
  font-style: italic;
}
</style>
