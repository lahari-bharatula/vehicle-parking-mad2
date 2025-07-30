<template>
  <div class="login-container">
    <div class="login-box">
      <h1>Login</h1>
      <form @submit.prevent="handleLogin">
        <label for="email">Email:</label>
        <input type="email" id="email" v-model="email" required />

        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" required />

        <button type="submit">Login</button>
      </form>
      
      <p class="register-link">
        Don't have an account?
        <router-link to="/signup">Click here to register</router-link>
      </p>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      errorMessage: '',
    };
  },
  methods: {
    handleLogin() {
      
      const postData = {
        email: this.email,
        password: this.password,
      };
      
      
      fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      })
        .then(async (response) => {
          if (!response.ok) {
            if (response.status === 404) {
              this.errorMessage = 'Account does not exist. Please register.';
            } else if (response.status === 401) {
              this.errorMessage = 'Invalid credentials.';
            } else {
              this.errorMessage = 'Login failed. Please try again.';
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          return await response.json();
        })
        .then((data) => {
          // Success path
          localStorage.setItem('token', data.token);
          localStorage.setItem(
            'user',
            JSON.stringify({
              email: data.user.email,
              name: data.user.name,
              vehicleno: data.user.vehicleno,
            })
          );



          if (data.user.role === 'user') {
            this.$router.push('/userdash');
          } else {
            this.$router.push('/adminDash');
          }
        })
        .catch((error) => {
          console.error('Login error:', error);
        });
    },
  },
};
</script>


<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 80px); /* Adjusted for navbar height */
  padding: 2rem;
}

.login-box {
  max-width: 400px;
  width: 100%;
  background-color: var(--color-primary);
  color: var(--color-text);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.error {
  color: red;
  margin-top: 1rem;
  text-align: center;
}

.register-link {
  margin-top: 1rem;
  text-align: center;
  color: var(--color-background);
}

.register-link a {
  color: var(--color-accent); 
}


.register-link a:hover {
  color: var(--color-background); 
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
</style>
