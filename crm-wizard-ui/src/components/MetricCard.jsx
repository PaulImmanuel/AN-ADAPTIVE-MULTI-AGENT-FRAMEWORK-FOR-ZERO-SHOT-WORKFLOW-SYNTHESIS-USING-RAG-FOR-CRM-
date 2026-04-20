import React, { useState, useEffect } from 'react';
import axios from 'axios';

function MetricCard() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/metrics/revenue')
      .then(res => setMetrics(res.data))
      .catch(err => console.error(err));
  }, []);

  if (!metrics) return <div>Loading Stats...</div>;

  // Simple grid style
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', padding: '10px' }}>
      <div style={cardStyle}>
        <h4 style={{margin: 0, color: '#666'}}>Total Revenue</h4>
        <h2 style={{margin: '5px 0', color: '#28a745'}}>{metrics.total_revenue}</h2>
      </div>
      <div style={cardStyle}>
        <h4 style={{margin: 0, color: '#666'}}>Active Users</h4>
        <h2 style={{margin: '5px 0', color: '#007bff'}}>{metrics.active_users}</h2>
      </div>
      <div style={cardStyle}>
        <h4 style={{margin: 0, color: '#666'}}>Monthly Growth</h4>
        <h2 style={{margin: '5px 0', color: '#6f42c1'}}>{metrics.growth}</h2>
      </div>
      <div style={cardStyle}>
        <h4 style={{margin: 0, color: '#666'}}>Churn Rate</h4>
        <h2 style={{margin: '5px 0', color: '#dc3545'}}>{metrics.churn_rate}</h2>
      </div>
    </div>
  );
}

const cardStyle = {
  background: '#f8f9fa', padding: '15px', borderRadius: '8px', border: '1px solid #ddd', textAlign: 'center'
};

export default MetricCard;