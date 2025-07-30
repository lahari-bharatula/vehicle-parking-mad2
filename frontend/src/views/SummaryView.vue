<template>
  <div class="summary-chart">
    <h2>Occupancy Summary</h2>
    <canvas id="summaryChart"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'SummaryView',
  async mounted() {
    const token = localStorage.getItem('token');
    const res = await fetch('http://127.0.0.1:5000/lots', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await res.json();
    const lots = data['parking_lots'];

    const labels = lots.map(lot => `Lot ${lot.lot}`);
    const occupied = lots.map(lot => lot.capacity - lot.available);
    const available = lots.map(lot => lot.available);

    new Chart(document.getElementById('summaryChart'), {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Occupied',
            data: occupied,
            backgroundColor: '#f87171'
          },
          {
            label: 'Available',
            data: available,
            backgroundColor: '#4ade80'
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        }
      }
    });
  }
}
</script>

<style scoped>
.summary-chart {
  padding: 30px;
}
canvas {
  max-width: 700px;
  margin: auto;
}
</style>
