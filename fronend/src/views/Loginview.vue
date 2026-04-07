<template>
  <div class="container">
    <h2>{{ isLogin ? 'Login' : 'Register' }}</h2>

    <input v-model="username" placeholder="Username" />
    <input v-model="password" type="password" placeholder="Password" />

    <button @click="submit">{{ isLogin ? 'Login' : 'Register' }}</button>

    <p @click="isLogin = !isLogin" style="cursor:pointer; color:blue;">
      {{ isLogin ? "Don't have an account? Register" : "Already have an account? Login" }}
    </p>

    <p v-if="message" style="color:red;">{{ message }}</p>
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
      isLogin: true,
    }
  },
  methods: {
    async submit() {
      try {
        const endpoint = this.isLogin ? '/api/login/' : '/api/register/'
        const response = await api.post(endpoint, {
          username: this.username,
          password: this.password,
        })

        // Save token to browser storage
        localStorage.setItem('access_token', response.data.access)

        this.message = response.data.message
        this.$router.push('/chat')  // go to chat page

      } catch (error) {
        this.message = error.response?.data?.error || 'Something went wrong'
      }
    }
  }
}
</script>

<style scoped>
.container {
  max-width: 400px;
  margin: 100px auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
input {
  padding: 8px;
  font-size: 16px;
}
button {
  padding: 10px;
  background: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
}
</style>