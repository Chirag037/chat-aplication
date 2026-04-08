<template>
  <div class="container">
    <div class="card">
      <h2>{{ isLogin ? 'Login' : 'Register' }}</h2>
      
      <form @submit.prevent="submit">
        <div class="input-group">
          <label>Username</label>
          <input v-model="username" placeholder="Enter username" required />
        </div>
        
        <div class="input-group">
          <label>Password</label>
          <input v-model="password" type="password" placeholder="Enter password" required />
        </div>

        <button type="submit" :disabled="loading" class="btn">
          {{ loading ? 'Processing...' : (isLogin ? 'Login' : 'Register') }}
        </button>
      </form>

      <p @click="isLogin = !isLogin" class="toggle-link">
        {{ isLogin ? "Don't have an account? Register" : "Already have an account? Login" }}
      </p>

      <p v-if="message" :class="['message', messageType]">{{ message }}</p>
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
      message: '',
      messageType: 'error',
      isLogin: true,
      loading: false,
    }
  },
  methods: {
    async submit() {
      if (!this.username || !this.password) {
        this.message = 'Please fill in all fields'
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

        // Save token to browser storage
        if (response.data.access) {
          localStorage.setItem('access_token', response.data.access)
          localStorage.setItem('username', this.username)
        }

        this.message = response.data.message || (this.isLogin ? 'Login successful!' : 'Account created!')
        this.messageType = 'success'

        // Redirect after a short delay
        setTimeout(() => {
          this.$router.push('/chat')
        }, 1000)

      } catch (error) {
        console.error('Submission error:', error)
        this.message = error.response?.data?.error || error.response?.data?.message || 'Something went wrong. Please try again.'
        this.messageType = 'error'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.input-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
}

.btn {
  width: 100%;
  padding: 0.75rem;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: background 0.2s;
  margin-top: 1rem;
}

.btn:hover:not(:disabled) {
  background: #45a049;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.toggle-link {
  text-align: center;
  margin-top: 1rem;
  cursor: pointer;
  color: #2196F3;
  font-size: 0.9rem;
}

.toggle-link:hover {
  text-decoration: underline;
}

.message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 4px;
  text-align: center;
  font-size: 0.9rem;
}

.error {
  background-color: #ffebee;
  color: #c62828;
}

.success {
  background-color: #e8f5e9;
  color: #2e7d32;
}
</style>