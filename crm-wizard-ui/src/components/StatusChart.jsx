import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

function StatusChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    // 1. Fetch data from our new API endpoint
    axios.get('http://127.0.0.1:8000/api/tickets/status-overview')
      .then(response => {
        // 2. Format the data for the chart library
        const labels = response.data.map(item => item.ticket_status);
        const data = response.data.map(item => item.count);

        setChartData({
          labels: labels,
          datasets: [{
            label: 'Ticket Status',
            data: data,
            backgroundColor: [
              'rgba(255, 99, 132, 0.2)',
              'rgba(54, 162, 235, 0.2)',
              'rgba(255, 206, 86, 0.2)',
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
            ],
            borderWidth: 1,
          }],
        });
      })
      .catch(error => console.error("Error fetching chart data:", error));
  }, []); // The empty array means this runs once when the component mounts

  if (!chartData) {
    return <div>Loading Status Chart...</div>;
  }

  // 3. Render the chart with live data
  return (
    <div style={{ padding: '20px', width: '300px' }}>
      <h3>Ticket Status Overview</h3>
      <Doughnut data={chartData} />
    </div>
  );
}

export default StatusChart;