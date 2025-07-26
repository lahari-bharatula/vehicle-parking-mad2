<template>
  <div class="register-container">
    <h2>Register</h2>

    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="name">Name:</label>
        <input v-model="name" type="text" id="name" required />
      </div>

      <div class="form-group">
        <label for="email">Email:</label>
        <input v-model="email" type="email" id="email" required />
      </div>

      <div class="form-group">
        <label for="password">Password:</label>
        <input v-model="password" type="password" id="password" required />
      </div>

      <button type="submit">Register</button>

      <p class="login-link">
        Already have an account?
        <router-link to="/login">Click here to login</router-link>
      </p>
    </form>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <p v-if="successMessage" class="success">{{ successMessage }}</p>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      name: '',
      email: '',
      password: '',
      errorMessage: '',
      successMessage: '',
    };
  },
  methods: {
    handleRegister() {
      const postData = {
        name: this.name,
        email: this.email,
        password: this.password,
      };

      fetch('http://127.0.0.1:5000/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData),
      })
        .then(async (response) => {
          const data = await response.json();

          if (!response.ok) {
            this.errorMessage = data.error || 'Registration failed.';
            this.successMessage = '';
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          this.successMessage = 'Registration successful. You can now log in!';
          this.errorMessage = '';

          setTimeout(() => {
            this.$router.push('/login');
          }, 1500);
        })
        .catch((error) => {
          console.error('Register error:', error);
        });
    },
  },
};
</script>

<style scoped>
.register-container {
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
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
}

button:hover {
  background-color: #218838;
}

.login-link {
  margin-top: 15px;
  text-align: center;
}

.error {
  color: red;
  text-align: center;
  margin-top: 10px;
}

.success {
  color: green;
  text-align: center;
  margin-top: 10px;
}
</style>
