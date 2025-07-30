<template>
  <div class="navbar">
    <button class="profile-button" @click="toggleProfile">Profile</button>

    <div v-if="showProfile" class="profile-card">
      <p><strong>Name:</strong> {{ user.name }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Vehicle No:</strong> {{ user.vehicleno }}</p>
      <button @click="logout" class="logout-button">Logout</button>
    </div>
  </div>

  <div class="dashboard-container">
    <div class="dashboard-card">
      <h2>Welcome, <span class="username">{{ userName }}</span>!</h2>
      <p class="subtitle">Ready to book a service?</p>
      <button @click="goToBooking" class="book-btn">Book a Service</button> <br></br>
      <button @click="goToChartSummary" class="chart-btn">📊 View My Chart Summary</button>

      <hr class="divider" />

      <div v-if="reservations.length > 0" class="reservations-section">
        <h3>Your Reservations</h3>
        <ul class="reservation-list">
          <li v-for="res in reservations" :key="res.reservation_id" class="reservation-item">
            <div>
              <strong>Spot:</strong> {{ res.spot_id }} |
              <strong>Lot:</strong> {{ res.lot_id }} |
              <strong>From:</strong> {{ formatDate(res.parked_at) }} |
              <strong>Status:</strong>
              <span v-if="res.leaving_timestamp">
                Left: {{ formatDate(res.leaving_timestamp) }}
              </span>
              <span v-else>Active</span> |
              <span v-if="res.parking_cost">₹{{ res.parking_cost }}</span>
            </div>
            <button
              v-if="!res.leaving_timestamp"
              @click="vacateSpot(res.reservation_id)"
              class="vacate-btn">
              Vacate
            </button>
          </li>
        </ul>
      </div>

      <button @click="exportReport" class="export-btn">📄 Export My Parking History</button>
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
      showProfile: false,
      user: {
        name: '',
        email: '',
        vehicleno: ''
      }
    };
  },
  methods: {
    toggleProfile() {
      this.showProfile = !this.showProfile;
    },
    goToBooking() {
      this.$router.push('/booking');
    },
    goToChartSummary() {
      this.$router.push('/user/charts');
    },
    logout() {
      localStorage.clear();
      window.location.href = '/';
    },
    async exportReport() {
      try {
        const response = await fetch('http://localhost:5000/report', {
          method: 'GET',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        const data = await response.json();

        if (response.ok) {
          alert("Report generated! Click OK to download.");
          window.open(data.url, '_blank');
        } else {
          alert("Error: " + data.msg);
        }
      } catch (error) {
        console.error(error);
        alert("Something went wrong");
      }
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
          this.fetchReservations();
        } else {
          alert(data.msg || 'Failed to vacate spot.');
        }
      } catch (err) {
        console.error('Vacate failed:', err);
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString();
    },
  },
  mounted() {
    const storedUser = JSON.parse(localStorage.getItem('user'));
    if (storedUser) {
      this.user = storedUser;
      this.userName = this.user.name || 'User';
    } else {
      this.userName = 'User';
    }

    this.fetchReservations();
  }
};
</script>


<style scoped>

.chart-btn {
  margin-top: 10px;
  background-color: var(--color-secondary);
  color: white;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.chart-btn:hover {
  background-color: var(--color-accent)
}

.dashboard-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
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

.export-btn {
  background-color: var(--color-accent);
  color: var(--color-text);
  border: none;
  padding: 10px 16px;
  margin-top: 10px;
  border-radius: 4px;
  cursor: pointer;
}

.export-btn:hover {
  background-color: var(--color-secondary);
}

.logout-button:hover {
  background-color: #c00;
}
.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.greeting {
  margin: 0;
  color: var(--color-text);
}

.username {
  color: var(--color-primary);
}

.navbar {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.profile-button {
  position: absolute;
  top: 10px;
  right: 20px;
  background-color: var(--color-secondary);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.profile-button:hover {
  background-color: var(--color-accent);
}

.profile-card {
  position: absolute;
  top: 50px;
  right: 20px;
  background-color: var(--color-background);
  color: var(--color-text);
  border-radius: 10px;
  padding: 15px 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  z-index: 100;
  width: 230px;
  pointer-events: auto;
  border: 1px solid var(--color-primary);
}

.dashboard-card {
  background: var(--color-background);
  padding: 25px 30px;
  margin-top: 20px;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}
.dashboard-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.greeting {
  margin: 0;
  color: var(--color-text);
}

.username {
  color: var(--color-primary);
}


.subtitle {
  color: var(--color-text);
  margin-bottom: 20px;
}
.summary-btn{
  padding: 10px 25px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
}

.summary-btn:hover {
  background-color: var(--color-secondary);
}

.book-btn {
  padding: 10px 25px;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
}


.book-btn:hover {
  background-color: var(--color-secondary);
}

.divider {
  margin: 25px 0;
  border: none;
  height: 1px;
  background-color: #ddd;
}

.reservations-section h3 {
  margin-bottom: 15px;
  color: var(--color-text);
}

.reservation-list {
  list-style: none;
  padding: 0;
}


.reservation-item {
  background-color: var(--color-accent);
  margin-bottom: 15px;
  padding: 15px;
  border-left: 5px solid var(--color-primary);
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vacate-btn {
  background-color: #d9534f;
  color: white;
  padding: 6px 14px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.vacate-btn:hover {
  background-color: #c9302c;
}
</style>