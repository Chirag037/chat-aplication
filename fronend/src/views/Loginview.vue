<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-900 relative overflow-hidden font-sans">
    <!-- Subtle Professional Background -->
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(17,24,39,1)_0%,rgba(15,23,42,1)_100%)]"></div>
    <div class="absolute inset-0 opacity-20 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')]"></div>

    <div class="relative z-10 w-full px-4 py-8 flex justify-center">
      <div class="w-full max-w-md bg-slate-800/50 backdrop-blur-xl border border-white/5 rounded-2xl shadow-2xl p-8 md:p-10 transition-all duration-300">
        
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="inline-flex items-center justify-center w-14 h-14 bg-indigo-600 rounded-xl shadow-lg mb-4">
            <span class="text-white text-2xl font-bold">C</span>
          </div>
          <h2 class="text-2xl font-bold text-white tracking-tight">
            {{ isLogin ? 'Sign In' : 'Create Account' }}
          </h2>
          <p class="text-slate-400 mt-2 text-sm font-medium">
            {{ isLogin ? 'Access your workspace' : 'Get started with your new account' }}
          </p>
        </div>

        <!-- Form -->
        <form @submit.prevent="submit" class="space-y-5">
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Username</label>
            <div class="relative group">
              <input 
                v-model="username" 
                type="text"
                placeholder="Enter your username" 
                required 
                class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all duration-300"
              />
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Password</label>
            <div class="relative group">
              <input 
                v-model="password" 
                type="password" 
                placeholder="••••••••" 
                required 
                class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all duration-300"
              />
            </div>
          </div>

          <!-- Repeat Password (only for register) -->
          <transition 
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 -translate-y-4"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-4"
          >
            <div v-if="!isLogin">
              <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Repeat Password</label>
              <div class="relative group">
                <input 
                  v-model="confirmPassword" 
                  type="password" 
                  placeholder="••••••••" 
                  required 
                  class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 outline-none focus:border-purple-500 focus:ring-4 focus:ring-purple-500/10 transition-all duration-300"
                />
              </div>
            </div>
          </transition>

          <button 
            type="submit" 
            :disabled="loading" 
            class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3.5 rounded-xl shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
          >
            <span v-if="!loading">{{ isLogin ? 'Sign In' : 'Sign Up' }}</span>
            <div v-else class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 text-white mr-3" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </div>
          </button>
        </form>

        <!-- Toggle Button -->
        <div class="mt-8 text-center">
          <p class="text-gray-400 text-sm">
            {{ isLogin ? "New here?" : "Joined us before?" }}
            <button 
              @click="toggleMode" 
              class="text-purple-400 font-bold hover:text-purple-300 transition-colors duration-200 ml-1"
            >
              {{ isLogin ? 'Create an account' : 'Sign in to your account' }}
            </button>
          </p>
        </div>

        <!-- Notification Message -->
        <transition name="fade">
          <div 
            v-if="message" 
            :class="[
              'mt-6 p-4 rounded-xl text-center text-sm font-medium border flex items-center justify-center gap-2', 
              messageType === 'success' ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
            ]"
          >
            <span v-if="messageType === 'success'">✓</span>
            <span v-else>⚠️</span>
            {{ message }}
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      message: '',
      messageType: 'error',
      isLogin: true,
      loading: false,
    }
  },
  methods: {
    toggleMode() {
      this.isLogin = !this.isLogin;
      this.message = '';
      this.password = '';
      this.confirmPassword = '';
    },
    async submit() {
      // Basic validation
      if (!this.username || !this.password) {
        this.message = 'Please fill in all required fields'
        this.messageType = 'error'
        return
      }

      // Password confirmation check
      if (!this.isLogin && this.password !== this.confirmPassword) {
        this.message = 'Passwords do not match'
        this.messageType = 'error'
        return
      }

      this.loading = true
      this.message = ''
      
      try {
        const endpoint = this.isLogin ? '/api/login/' : '/api/register/'
        const response = await api.post(endpoint, {
          username: this.username,
          password: this.password,
        })

        if (response.data.access) {
          localStorage.setItem('access_token', response.data.access)
          localStorage.setItem('username', this.username)
        }

        this.message = response.data.message || (this.isLogin ? 'Successfully logged in!' : 'Welcome! Account created.')
        this.messageType = 'success'

        // Success redirection
        setTimeout(() => {
          this.$router.push('/chat')
        }, 1200)

      } catch (error) {
        console.error('Submission error:', error)
        this.message = error.response?.data?.error || error.response?.data?.message || 'Connection lost. Please try again.'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>