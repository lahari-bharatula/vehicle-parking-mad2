<template>
  <div class="signup-container">
    <div class="signup-box">
      <h1>Sign Up</h1>
      <form @submit.prevent="handleSignup">
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="name" required />

        <label for="email">Email:</label>
        <input type="email" id="email" v-model="email" required />

        <label for="vehicleno">Vehicle Number:</label>
        <input type="text" id="vehicleno" v-model="vehicleno" required />

        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? 'Registering...' : 'Register' }}
        </button>
      </form>

      <p class="login-link">
        Already have an account?
        <router-link to="/">Click here to login</router-link>
      </p>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignUpView',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      vehicleno: '',
      errorMessage: '',
      isLoading: false,
    };
  },
  methods: {
    handleSignup() {
      this.isLoading = true;
      this.errorMessage = '';

      const postData = {
        name: this.name.trim(),
        email: this.email.trim(),
        password: this.password,
        vehicleno: this.vehicleno.trim(),
      };

      fetch('http://127.0.0.1:5000/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      })
        .then(async (response) => {
          this.isLoading = false;

          if (!response.ok) {
            if (response.status === 409) {
              this.errorMessage = 'Email already registered.';
            } else {
              this.errorMessage = 'Signup failed. Please try again.';
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          return await response.json();
        })
        .then((data) => {
          alert('Signup successful! Please login.');
          this.$router.push('/');
        })
        .catch((error) => {
          console.error('Signup error:', error);
        });
    },
  },
};
</script>

<style scoped>
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 80px);
  padding: 2rem;
}

.signup-box {
  max-width: 400px;
  width: 100%;
  background-color: var(--color-primary);
  color: var(--color-text);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  margin-bottom: 1.5rem;
}

form {
  display: flex;
  flex-direction: column;
}

label {
  margin-top: 1rem;
  font-weight: bold;
}

input {
  padding: 0.5rem;
  margin-top: 0.25rem;
  border: 1px solid var(--color-accent);
  border-radius: 4px;
  font-size: 1rem;
}

button {
  margin-top: 2rem;
  padding: 0.75rem;
  font-size: 1rem;
  background-color: var(--color-secondary);
  color: var(--color-background);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: var(--color-accent);
}

.login-link {
  margin-top: 1rem;
  text-align: center;
  color: var(--color-background);
}

.error {
  margin-top: 1rem;
  color: red;
  text-align: center;
}
</style>
