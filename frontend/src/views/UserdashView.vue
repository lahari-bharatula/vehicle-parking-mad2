<template>
  <div class="dashboard-container">
    <h2>Welcome, {{ userName }}!</h2>
    
    <p>Ready to book a service?</p>
    <button @click="goToBooking">Book a Service</button>

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
          <button 
            v-if="!res.leaving_timestamp"
            @click="vacateSpot(res.id)">
            Vacate
          </button>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserDashboard',
  data() {
    return {
      userName: '',
      reservations: [],
    };
  },
  methods: {
    goToBooking() {
      this.$router.push('/booking');
    },
    async fetchReservations() {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch('http://127.0.0.1:5000/reservations', {
          method: 'GET',
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
      } catch (err) {
        console.error('Error fetching reservations:', err);
      }
    },
    async vacateSpot(reservationId) {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`http://127.0.0.1:5000/reservations/${reservationId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await res.json();
        if (res.ok) {
          alert('Spot vacated successfully!');
          this.fetchReservations(); // Refresh the list
        } else {
          alert(data.msg || 'Failed to vacate spot.');
        }
      } catch (err) {
        console.error('Vacate failed:', err);
      }
    },
  },
  mounted() {
    const storedEmail = localStorage.getItem('user_email');
    if (storedEmail) {
      this.userName = storedEmail.split('@')[0];
    } else {
      this.userName = 'Userrr';
    }

    this.fetchReservations();
  },
};
</script>