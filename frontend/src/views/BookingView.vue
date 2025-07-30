<template>
  <div class="booking-container">
    <!-- Top Bar -->
    <div class="top-bar">
      <h2>Book a Parking Spot</h2>
      <div class="profile-wrapper">
        <button class="profile-button" @click="toggleProfilePopup">
          👤
        </button>
        <div v-if="showProfile" class="profile-popup">
          <p><strong>Email:</strong> {{ user.email }}</p>
          <p><strong>Vehicle No:</strong> {{ user.vehicleno }}</p>
          <button @click="logout" class="logout-button">Logout</button>
        </div>
      </div>
    </div>

    <form @submit.prevent="bookReservation">
      <label for="lot">Select Parking Lot:</label>
      <select v-model="selectedLotId" required>
        <option disabled value="">-- Select Lot --</option>
        <option v-for="lot in lotOptions" :key="lot.id" :value="lot.lot">
         {{ lot.area }}
        </option>
      </select>

      <div class="button-group">
    <button type="submit">Book Now</button>
    <button type="button" @click="goHome">Home</button>
  </div>

    </form>

    <p v-if="message" :class="{ success: isSuccess, error: !isSuccess }">
      {{ message }}
    </p>

    <hr />

    <div v-if="reservations.length > 0">
      <h3>Your Reservations</h3>
      <ul>
        <li v-for="res in reservations" :key="res.id">
          Spot: {{ res.spot_id }} |
          Lot: {{ res.lot_id }} |
          From: {{ res.parking_timestamp }} |
          {{ res.leaving_timestamp ? 'Left: ' + res.leaving_timestamp : 'Active' }} |
          {{ res.parking_cost ? '₹' + res.parking_cost : '' }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookingView',
  data() {
  return {
    selectedLotId: '',
    lotOptions: [],
    message: '',
    isSuccess: false,
    reservations: [],
    showProfile: false, 
    user: {              
      email: '',
      vehicleno: '',
    },
  };
},

  methods: {
    async fetchLots() {
        const token = localStorage.getItem('token');
      try {
       const res = await fetch('http://127.0.0.1:5000/lots', {
        method: 'GET',
        headers: {
        Authorization: `Bearer ${token}`,
      },
        });

        const data = await res.json();

        if (res.ok) {
          this.lotOptions = data["parking_lots"];
        } else {
          console.warn('Failed to load lots:', data);
        }
      } catch (err) {
        console.error('Error fetching parking lots:', err);
      }
    },

     goHome() {
    this.$router.push('/userdash');
  },

    async bookReservation() {
      this.message = '';
      const token = localStorage.getItem('token');

      try {
        const response = await fetch('http://127.0.0.1:5000/reservations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ lot_id: this.selectedLotId }),
        });

        const data = await response.json();

        if (!response.ok) {
          this.isSuccess = false;
          this.message = data.msg || 'Booking failed.';
          return;
        }

        this.isSuccess = true;
        this.message = `Booking successful! Reservation ID: ${data.reservation_id}`;
        this.fetchReservations(); // Refresh list
      } catch (err) {
        this.isSuccess = false;
        this.message = 'Error booking reservation.';
        console.error(err);
      }
    },

    async fetchReservations() {
      const token = localStorage.getItem('token');

      try {
        const res = await fetch('http://127.0.0.1:5000/reservations', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await res.json();
        if (res.ok) {
          this.reservations = data.reservations || [];
        } else {
          console.warn('Failed to load reservations', data);
        }
      } catch (error) {
        console.error('Fetch error:', error);
      }
    },
  },

  mounted() {
    this.fetchLots();
    this.fetchReservations();
  },
};
</script>

<style scoped>
.booking-container {
  max-width: 700px;
  margin: 60px auto;
  padding: 30px;
  background: var(--color-primary);
  border-radius: 12px;
  font-family: 'Segoe UI', sans-serif;
  box-shadow: 0 4px 12px rgba(0, 0, 80, 0.1);
  position: relative;
}

/* Top Bar */
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-wrapper {
  position: relative;
}

.profile-button {
  background-color: var(--color-accent);
  color: #fff;
  border: none;
  border-radius: 50%;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 20px;
}

.profile-popup {
  position: absolute;
  top: 36px;
  right: 0;
  background: var(--color-background);
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px 14px;
  width: 220px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.logout-button {
  background-color: #d33;
  color: white;
  border: none;
  padding: 6px 10px;
  margin-top: 10px;
  border-radius: 4px;
  cursor: pointer;
}

.logout-button:hover {
  background-color: #b22;
}

form {
  margin: 20px 0;
}

select {
  margin: 10px 0;
  padding: 10px;
  font-size: 16px;
  border-radius: 6px;
  border: 1px solid #ccc;
  width: 100%;
}

button[type="submit"] {
  padding: 12px 20px;
  font-size: 16px;
  background-color: #6a5acd;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
}

button[type="submit"]:hover {
  background-color: #5b4fc3;
}

button[type="button"] {
  padding: 12px 20px;
  font-size: 16px;
  background-color: #6a5acd;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 10px;
  margin-left: 10px;
}

button[type="button"]:hover {
  background-color: #5b4fc3;        
}

.success {
  color: green;
  margin-top: 10px;
}

.error {
  color: red;
  margin-top: 10px;
}
</style>
