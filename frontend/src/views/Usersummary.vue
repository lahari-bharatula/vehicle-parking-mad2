<template>
  <div>
    <h2>📊 Your Parking Summary</h2>
    <canvas id="user-chart" width="400" height="200"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'UserSummary',
  async mounted() {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:5000/user/charts', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      const data = await response.json();

      if (!response.ok) {
        alert(data.msg || "Failed to fetch chart data.");
        return;
      }

      const ctx = document.getElementById('user-chart');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'Hours Parked per Day',
            data: data.data,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    } catch (err) {
      console.error("Chart load error", err);
    }
  }
};
</script>

<style scoped>
.user-summary {
  padding: 20px;
  background-color: #081c2c;
  color: white;
}

canvas {
  width: 100% !important;
  height: 300px !important;
}

</style>
