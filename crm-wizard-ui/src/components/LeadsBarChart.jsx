import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function LeadsBarChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/leads/sources')
      .then(response => {
        setChartData({
          labels: response.data.labels,
          datasets: [{
            label: 'Leads per Source',
            data: response.data.data,
            backgroundColor: 'rgba(54, 162, 235, 0.6)',
          }],
        });
      });
  }, []);

// ... imports and logic ...

  if (!chartData) return <div>Loading Leads Chart...</div>;

  return (
    // Use a flex container to center the chart and give it a max-height
    <div style={{ 
      padding: '20px', 
      height: '350px', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#fff', // Optional: White background for contrast
      borderRadius: '8px'      // Optional: Rounded corners
    }}>
      <h3 style={{ marginBottom: '15px', color: '#333' }}>Marketing Lead Sources</h3>
      
      {/* Wrapper div specifically for Chart.js to control size */}
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        <Bar 
          data={chartData} 
          options={{ 
            responsive: true, 
            maintainAspectRatio: false, // This is key! Lets it fill the container
            plugins: {
              legend: { position: 'bottom' } // Moves legend to bottom for neatness
            }
          }} 
        />
      </div>
    </div>
  );
}

export default LeadsBarChart;
