import React, { useState, useEffect } from 'react';
import axios from 'axios';

function RecentTicketsTable() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Fetch data from our new API endpoint
    axios.get('http://127.0.0.1:8000/api/tickets/recent')
      .then(response => {
        setTickets(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching recent tickets:", error);
        setLoading(false);
      });
  }, []); // The empty array means this runs once

  if (loading) {
    return <div>Loading Recent Tickets...</div>;
  }

  // --- Style definitions for clarity ---
  const tableStyle = {
    width: '100%',
    borderCollapse: 'collapse', // This makes borders look cleaner
    fontFamily: 'Arial, sans-serif' // Added for a cleaner look
  };

  // --- UPDATED THIS STYLE ---
  const thStyle = {
    border: '1px solid #ddd',
    padding: '12px 8px',
    background: '#343a40', // A nice dark gray background
    color: '#ffffff',     // White text color for contrast
    textAlign: 'left'      // Align text to the left
  };

  const tdStyle = {
    border: '1px solid #ddd',
    padding: '8px'
  };

  // 3. Render the table with live data
  return (
    <div style={{ padding: '20px' }}>
      <h3>Recent Tickets</h3>
      <table style={tableStyle}>
        <thead>
          {/* The inline background style here is no longer needed, 
              but it doesn't hurt to leave it. The `thStyle` will override it. */}
          <tr style={{ background: '#f4f4f4' }}>
            <th style={thStyle}>Customer</th>
            <th style={thStyle}>Subject</th>
            <th style={thStyle}>Status</th>
            <th style={thStyle}>Priority</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket, index) => (
            <tr key={index}>
              <td style={tdStyle}>{ticket.customer_name}</td>
              <td style={tdStyle}>{ticket.ticket_subject}</td>
              <td style={tdStyle}>{ticket.ticket_status}</td>
              <td style={tdStyle}>{ticket.ticket_priority}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default RecentTicketsTable;