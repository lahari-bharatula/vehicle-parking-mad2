<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div id="app">
    <!-- Logo and message (shown on every page) -->
    <header class="app-header">
      <img src="@/assets/logo.png" alt="Logo" class="logo" />
      <div class="welcome-text">
        <h1>Welcome!</h1>
        <p>Parking app :)</p>
      </div>
    </header>
    <!-- This will render the current route -->
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: #111;
  color: white;
  font-family: sans-serif;
}

.left-panel {
  flex: 1.2; /* make this side a bit wider */
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-right: 1px solid #333;
}

.right-panel {
  flex: 1.8;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.logo {
  height: 120px;
  margin-bottom: 30px;
}

.welcome-text {
  text-align: center;
}

.welcome-text h1 {
  color: #4caf50;
  font-size: 32px;
  margin: 0 0 10px;
}

.welcome-text p {
  font-size: 18px;
  color: #ccc;
}
</style>
