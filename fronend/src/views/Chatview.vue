<template>
  <div>
    <h1>Welcome to Chat! 🎉</h1>
    <button @click="logout">Logout</button>
  </div>
</template>

<script>
export default {
  mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('access_token')
      this.$router.push('/')
    }
  }
}
</script>