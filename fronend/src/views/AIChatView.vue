<template>
  <div class="flex h-screen bg-white overflow-hidden font-sans text-slate-900 selection:bg-amber-100/60">
    <Sidebar
      :activeRoomId="null"
      :isOpen="isSidebarOpen"
      @select-room="handleRoomSelect"
      @close="isSidebarOpen = false"
    />

    <div class="flex-1 flex flex-col min-w-0 bg-white overflow-hidden">
      <header class="h-14 flex items-center justify-between px-6 bg-gradient-to-r from-amber-50 via-rose-50 to-amber-50 border-b border-amber-100 z-10 shrink-0">
        <div class="flex items-center gap-3">
          <button @click="isSidebarOpen = true" class="md:hidden p-2 -ml-2 text-amber-700 hover:bg-white/60 rounded-lg transition-colors" title="Open sidebar">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div>
            <h2 class="text-sm font-bold text-slate-900 tracking-tight">AI Chat</h2>
            <div class="flex items-center gap-1.5 py-0.5">
              <span class="w-1.5 h-1.5 bg-amber-400 rounded-full"></span>
              <span class="text-[9px] font-bold text-amber-800/70 uppercase tracking-[0.15em]">Ollama</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3 md:gap-6">
          <div class="hidden sm:flex items-center gap-3">
            <span class="text-[10px] font-bold text-amber-800/60 uppercase tracking-widest">{{ currentUser }}</span>
            <div class="w-7 h-7 bg-white/70 border border-amber-200/60 rounded-lg flex items-center justify-center text-[10px] font-bold text-amber-900">
              {{ getInitial(currentUser) }}
            </div>
          </div>
          <button @click="startNewConversation" class="text-[10px] font-bold text-indigo-700/80 hover:text-indigo-900 uppercase tracking-widest transition-colors duration-200">
            New Chat
          </button>
          <button @click="goToChat" class="text-[10px] font-bold text-amber-800/70 hover:text-amber-950 uppercase tracking-widest transition-colors duration-200">
            Back to Chat
          </button>
        </div>
      </header>

      <main ref="scroller" class="flex-1 overflow-y-auto p-4 md:p-6 bg-slate-50">
        <div class="max-w-3xl mx-auto space-y-4">
          <div v-for="(m, idx) in messages" :key="idx" :class="['flex', m.role === 'user' ? 'justify-end' : 'justify-start']">
            <div
              :class="[
                'max-w-[85%] rounded-2xl px-4 py-3 shadow-sm border text-sm leading-relaxed whitespace-pre-wrap',
                m.role === 'user'
                  ? 'bg-white border-amber-200/70 text-slate-900'
                  : 'bg-white border-slate-200 text-slate-800'
              ]"
            >
              <p class="font-semibold text-[11px] uppercase tracking-widest mb-1"
                 :class="m.role === 'user' ? 'text-amber-900/60' : 'text-slate-500'">
                {{ m.role === 'user' ? currentUser : 'AI' }}
              </p>
              <p>{{ m.content }}</p>
            </div>
          </div>

          <div v-if="loading" class="flex justify-start">
            <div class="bg-white border border-slate-200 rounded-2xl px-4 py-3 text-sm text-slate-500 shadow-sm">
              Thinking…
            </div>
          </div>

          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
            {{ error }}
          </div>
        </div>
      </main>

      <div class="border-t border-slate-100 bg-white px-4 md:px-6 py-4">
        <form class="max-w-3xl mx-auto flex items-end gap-3" @submit.prevent="send">
          <textarea
            v-model="draft"
            rows="1"
            placeholder="Ask anything…"
            class="flex-1 resize-none rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:ring-4 focus:ring-amber-200/40 focus:border-amber-300"
            @keydown.enter.exact.prevent="send"
            @keydown.enter.shift.exact.stop
          ></textarea>
          <button
            type="submit"
            class="h-11 px-4 rounded-xl bg-amber-600 text-white text-sm font-semibold shadow-sm hover:bg-amber-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            :disabled="!draft.trim() || loading"
          >
            Send
          </button>
        </form>
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
      currentUser: localStorage.getItem('username') || 'Guest',
      isSidebarOpen: false,
      draft: '',
      loading: false,
      error: '',
      messages: [],
      conversationId: null
    };
  },
  methods: {
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : '?';
    },
    goToChat() {
      this.$router.push('/chat');
    },
    handleRoomSelect(payload) {
      const room = typeof payload === 'object' ? payload : null;
      const rawId = room ? room.id : payload;
      const id = rawId != null ? String(rawId) : null;
      if (!id) return;
      localStorage.setItem('last_room_id', id);
      this.isSidebarOpen = false;
      this.$router.push('/chat');
    },
    async send() {
      const prompt = this.draft.trim();
      if (!prompt || this.loading) return;
      this.error = '';

      this.messages.push({ role: 'user', content: prompt });
      this.draft = '';
      this.loading = true;
      this.$nextTick(() => this.scrollToBottom());

      try {
        const res = await api.post('/api/ai/chat/', {
          model: 'llama3.2',
          prompt,
          system: 'You are a helpful, concise assistant.',
          conversation_id: this.conversationId
        });
        const conversation = res?.data?.conversation;
        const text = res?.data?.response || '';
        if (conversation?.id) this.conversationId = conversation.id;
        if (conversation?.messages?.length) {
          this.messages = conversation.messages.map(m => ({ role: m.role, content: m.content }));
        } else {
          this.messages.push({ role: 'assistant', content: String(text || 'No response.') });
        }
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to reach Ollama.';
        this.error = String(msg);
      } finally {
        this.loading = false;
        this.$nextTick(() => this.scrollToBottom());
      }
    },
    async loadConversation() {
      this.error = '';
      try {
        const res = await api.get('/api/ai/conversation/');
        const convo = res?.data || {};
        this.conversationId = convo.id || null;
        if (Array.isArray(convo.messages) && convo.messages.length > 0) {
          this.messages = convo.messages.map(m => ({ role: m.role, content: m.content }));
        } else {
          this.messages = [{ role: 'assistant', content: 'Hi! Ask me anything.' }];
        }
      } catch (e) {
        this.messages = [{ role: 'assistant', content: 'Hi! Ask me anything.' }];
      } finally {
        this.$nextTick(() => this.scrollToBottom());
      }
    },
    async startNewConversation() {
      this.error = '';
      this.loading = false;
      this.draft = '';
      try {
        const res = await api.post('/api/ai/conversation/new/', { title: 'AI Chat' });
        const convo = res?.data || {};
        this.conversationId = convo.id || null;
        this.messages = [{ role: 'assistant', content: 'Started a new conversation. Ask me anything.' }];
      } catch (e) {
        const msg = e?.response?.data?.error || e?.message || 'Failed to start a new conversation.';
        this.error = String(msg);
      } finally {
        this.$nextTick(() => this.scrollToBottom());
      }
    },
    scrollToBottom() {
      const el = this.$refs.scroller;
      if (!el) return;
      el.scrollTop = el.scrollHeight;
    }
  },
  mounted() {
    this.loadConversation();
  }
};
</script>
