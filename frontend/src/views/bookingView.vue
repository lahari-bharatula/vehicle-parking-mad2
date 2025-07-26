<template>
  <div class="booking-container">
    <h2>Book a Parking Spot</h2>

    <form @submit.prevent="bookReservation">
      <label for="lot">Select Parking Lot:</label>
      <select v-model="selectedLotId" required>
        <option disabled value="">-- Select Lot --</option>
        <option v-for="lot in lotOptions" :key="lot.id" :value="lot.lot">
          Lot #{{ lot.id }} - {{ lot.area }}
        </option>
      </select>

      <button type="submit">Book Now</button>
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
    };
  },
  methods: {
    async fetchLots() {
      try {
       const res = await fetch('http://127.0.0.1:5000/lots', {
        method: 'GET',
        });

        const data = await res.json();

        if (res.ok) {
          this.lotOptions = data["parking lots"];
        } else {
          console.warn('Failed to load lots:', data);
        }
      } catch (err) {
        console.error('Error fetching parking lots:', err);
      }
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
  max-width: 600px;
  margin: 60px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

form {
  margin-bottom: 20px;
}

select {
  margin: 10px 0;
  padding: 8px;
  font-size: 16px;
}

button {
  padding: 10px 16px;
  font-size: 16px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:hover {
  background-color: #3367d6;
}

.success {
  color: green;
}

.error {
  color: red;
}
</style>
