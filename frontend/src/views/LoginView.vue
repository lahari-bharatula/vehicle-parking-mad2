<template>
  
  <div class="login-container">
    <h2>Login</h2>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">Email:</label>
        <input v-model="email" type="email" id="email" required />
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input v-model="password" type="password" id="password" required />
      </div>

      <button type="submit">Login</button>

      <p class="register-link">
        Don't have an account?
        <router-link to="/register">Click here to register</router-link>
      </p>
    </form>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
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

          if (data.user.role === 'user') {
            this.$router.push('/userDash');
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
  max-width: 400px;
  margin: 100px auto;
  padding: 30px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
  font-family: Arial, sans-serif;
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 5px;
  font-weight: bold;
}

input {
  padding: 8px;
  font-size: 16px;
  border-radius: 4px;
  border: 1px solid #aaa;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background-color: #3367d6;
}

.register-link {
  margin-top: 15px;
  text-align: center;
}

.error {
  color: red;
  text-align: center;
  margin-top: 10px;
}
</style>
