import React from 'react';
import StatusChart from './components/StatusChart';
import RecentTicketsTable from './components/RecentTicketsTable';
import ChatWindow from './components/ChatWindow';
import MetricCard from './components/MetricCard';
import LeadsBarChart from './components/LeadsBarChart';

// This is the helper function that reads the JSON
// and decides which component to show.
function renderWidget(widget) {
  const widgetType = widget.type; 
  switch (widgetType) {
    case 'StatusChart': return <StatusChart />;
    case 'RecentTicketsTable': return <RecentTicketsTable />;
    // --- NEW CASES ---
    case 'MetricCard': return <MetricCard />;
    case 'LeadsBarChart': return <LeadsBarChart />;
    // ----------------
    default: return <div>Error: Unknown widget type "{widgetType}"</div>;
  }
}

// Your App.jsx is passing props named 'config' and 'onReset'
function Dashboard({ config, onReset }) {

  // This is the "spy" log from before. Leave it in for this test.
  console.log("DASHBOARD COMPONENT (src/Dashboard.jsx) RECEIVED THIS CONFIG:", config);

  if (!config || !config.tabs) {
    return <div>Loading Dashboard or invalid config...</div>;
  }

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: 'auto' }}>
      
      {/* 1. Add a 'Go Back' button that uses the 'onReset' prop from App.jsx */}
      <button onClick={onReset} style={{ marginBottom: '20px' }}>
        &larr; Back to Wizard
      </button>
      
      <h1>{config.dashboardTitle}</h1>
      <hr />

      {/* 2. Loop through the tabs from the AI's JSON */}
      {config.tabs.map((tab, tabIndex) => (
        <div key={tabIndex} style={{ marginBottom: '20px' }}>
          <h2>{tab.title}</h2>
          
          {/* This is the "spy" log */}
          {console.log("Looping over tab:", tab.title, "It has widgets:", tab.widgets)}

          {/* 3. Check if the 'widgets' array exists AND has items */}
          {tab.widgets && tab.widgets.length > 0 ? (
            
            // 4. Loop over the widgets and render each one
            tab.widgets.map((widget, widgetIndex) => (
              <div key={widgetIndex} style={{ marginBottom: '20px', border: '1px solid #ccc', borderRadius: '8px', padding: '10px' }}>
                
                {/* 5. This is where the magic happens! */}
                {renderWidget(widget)}

              </div>
            ))
          ) : (
            // 6. This is the "No content" message
            <p>No widgets to display for this tab.</p>
          )}
        </div>
      ))}
      <ChatWindow />
    </div>
  );
  
}

export default Dashboard;