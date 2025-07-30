<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <div class="container">
      <div class="left-panel">
        <img alt="Vue logo" class="logo" src="@/assets/image.png" width="125" height="125" />

          <div class="wrapper">
            <h1 class="parcar-title">Welcome to ParCar</h1>

             <nav>
                <RouterLink to="/about">About</RouterLink>
              </nav>
          </div> 
      </div>
    </div> 
  </header>

  <RouterView />
</template>

<style scoped>
/* Base app styling */
#app {
  background-color: var(--color-background);
  color: var(--color-text);
  font-family: 'Segoe UI', sans-serif;
  min-height: 100vh;
  padding: 1rem;
}

/* Layout container: splits page into left and right */
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  padding: 2rem;
  gap: 4rem;
  flex-wrap: wrap;
}

/* Left and right panel */
.left-panel, .right-panel {
  flex: 1;
  max-width: 500px;
}

/* Left panel content */
.left-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

/* Logo */
.logo {
  display: block;
  margin-bottom: 2rem;
}

/* Title styling */
.parcar-title {
  font-size: 2.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1.5rem;

  background: linear-gradient(to right, #BBBDF6, #9893DA, #797A9E);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  -webkit-text-fill-color: transparent;
}

/* Navigation styling */
nav {
  margin-top: 1rem;
  text-align: center;
}

nav a {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  margin: 0 0.5rem;
  background-color: var(--color-primary);
  color: var(--color-background);
  border: 2px solid var(--color-secondary);
  border-radius: 8px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s, color 0.3s;
}

nav a:hover {
  background-color: var(--color-accent);
  color: var(--color-text);
}

nav a.router-link-exact-active {
  background-color: var(--color-secondary);
  color: var(--color-background);
  border-color: var(--color-accent);
}

nav a:first-of-type {
  border-left: none;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
    padding: 2rem 1rem;
  }

  .left-panel, .right-panel {
    max-width: 100%;
  }
}
</style>
