import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './Dashboard';

// --- Pre-defined options for our dropdowns ---
const industryOptions = ["SaaS", "Real Estate", "E-commerce", "Consulting", "Health & Wellness","Customer Support", "Other"];
const pipelineOptions = {
  "Simple Sales": "Lead > Contacted > Meeting > Proposal > Closed",
  "SaaS Funnel": "Visitor > Trial Sign-up > Activated User > Subscribed",
  "Real Estate": "Inquiry > Viewing > Offer Made > Under Contract > Closed",
  "Custom": "Custom"
};
const goalOptions = [
  "Track leads more effectively",
  "Improve sales team collaboration",
  "Get better sales forecasts and analytics",
  "Manage support tickets",
  "Automate follow-up communication"
];


// --- The Wizard Component (standalone component, outside of App) ---
const Wizard = ({
  step,
  formData,
  error,
  isStepActive,
  isLoading,
  handleNext,
  handlePrev,
  handleChange,
  handleSubmit,
  customPipeline,
  setCustomPipeline
}) => {
  const renderStepContent = () => {
    switch (step) {
      case 1:
        return (
          <>
            <h2>Step 1: Company Basics</h2>
            <div className="input-group">
              <label htmlFor="company_name">Company Name</label>
              <input id="company_name" name="company_name" value={formData.company_name} onChange={handleChange} placeholder="e.g., Innovate Solutions Inc." />
            </div>
            <div className="input-group">
              <label htmlFor="industry">Industry</label>
              <select id="industry" name="industry" value={formData.industry} onChange={handleChange}>
                {industryOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
              </select>
            </div>
            <div className="button-group right-align">
              <button onClick={handleNext}>Next &rarr;</button>
            </div>
          </>
        );
      case 2:
        return (
          <>
            <h2>Step 2: Sales Process & Goals</h2>
            <div className="input-group">
              <label htmlFor="pipeline_stages">Sales Pipeline Stages</label>
              <select id="pipeline_stages" name="pipeline_stages" value={formData.pipeline_stages} onChange={handleChange}>
                {Object.entries(pipelineOptions).map(([key, value]) => <option key={key} value={value}>{key}</option>)}
              </select>
            </div>
            {formData.pipeline_stages === 'Custom' && (
              <div className="input-group custom-pipeline-input">
                <input
                  name="custom_pipeline_input"
                  value={customPipeline}
                  onChange={(e) => setCustomPipeline(e.target.value)}
                  placeholder="e.g., Lead > Qualified > Demo > Proposal > Closed"
                />
              </div>
            )}
            <div className="input-group">
              <label htmlFor="contact_info">Key Contact Fields</label>
              <input id="contact_info" name="contact_info" value={formData.contact_info} onChange={handleChange} placeholder="e.g., Name, Email, Phone, Lead Source" />
            </div>
            <div className="input-group">
              <label htmlFor="primary_goal">Primary Goal for this CRM</label>
              <select id="primary_goal" name="primary_goal" value={formData.primary_goal} onChange={handleChange}>
                {goalOptions.map(opt => <option key={opt} value={opt}>{opt}</option>)}
              </select>
            </div>
            <div className="button-group spaced">
              <button onClick={handlePrev}>&larr; Previous</button>
              <button onClick={handleSubmit} disabled={isLoading}>
                {isLoading ? 'Generating...' : 'Generate CRM'}
              </button>
            </div>
          </>
        );
      default:
        return <div>Loading...</div>;
    }
  };

  return (
    <div className="container">
      <h1>GenCRM Setup Wizard</h1>
      {error && <p className="error">{error}</p>}
      <div className={`wizard-box ${isStepActive ? 'active' : 'inactive'}`}>
        {renderStepContent()}
      </div>
    </div>
  );
};


// --- The Main App Component ---
function App() {
  const [view, setView] = useState('wizard');
  const [dashboardConfig, setDashboardConfig] = useState(null);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    company_name: '',
    industry: industryOptions[0],
    pipeline_stages: Object.values(pipelineOptions)[0],
    contact_info: 'Name, Email, Phone, Lead Source, Status',
    primary_goal: goalOptions[0],
  });
  const [customPipeline, setCustomPipeline] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStepActive, setIsStepActive] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setIsStepActive(true), 50);
    return () => clearTimeout(timer);
  }, [step]);

  const handleNext = () => {
    setIsStepActive(false);
    setTimeout(() => setStep(step + 1), 300);
  };

  const handlePrev = () => {
    setIsStepActive(false);
    setTimeout(() => setStep(step - 1), 300);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    const finalPipeline = formData.pipeline_stages === 'Custom' ? customPipeline : formData.pipeline_stages;
    const dataToSubmit = { ...formData, pipeline_stages: finalPipeline };
    try {
      const apiResponse = await axios.post('http://127.0.0.1:8000/api/generate-dashboard', dataToSubmit);
      if (apiResponse.data && apiResponse.data.status === 'success') {
        setDashboardConfig(apiResponse.data.config);
        setView('dashboard');
      } else {
        setError('Received an invalid response from the backend.');
      }
    } catch (err) {
      setError('Failed to generate dashboard. Is the backend server running?');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setView('wizard');
    setStep(1);
    setDashboardConfig(null);
    setFormData({
      company_name: '',
      industry: industryOptions[0],
      pipeline_stages: Object.values(pipelineOptions)[0],
      contact_info: 'Name, Email, Phone, Lead Source, Status',
      primary_goal: goalOptions[0],
    });
  };

  return (
    <div className={view === 'wizard' ? 'app-view-wizard' : 'app-view-dashboard'}>
      {view === 'wizard' ? (
        <Wizard
          step={step}
          formData={formData}
          error={error}
          isStepActive={isStepActive}
          isLoading={isLoading}
          handleNext={handleNext}
          handlePrev={handlePrev}
          handleChange={handleChange}
          handleSubmit={handleSubmit}
          customPipeline={customPipeline}
          setCustomPipeline={setCustomPipeline}
        />
      ) : (
        <Dashboard config={dashboardConfig} onReset={handleReset} />
      )}
    </div>
  );
}

export default App;