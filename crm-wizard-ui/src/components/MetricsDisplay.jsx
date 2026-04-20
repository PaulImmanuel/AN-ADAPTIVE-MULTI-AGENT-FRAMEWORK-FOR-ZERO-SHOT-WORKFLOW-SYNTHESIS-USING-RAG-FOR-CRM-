import React from 'react';
import { FiTrendingUp, FiTrendingDown, FiDollarSign } from 'react-icons/fi';

const iconMap = {
  default: FiTrendingUp,
  revenue: FiDollarSign,
  churn: FiTrendingDown,
};

const MetricsDisplay = ({ metrics }) => {
  return (
    <div className="metrics-grid">
      {metrics.map((metric) => {
        const Icon = metric.toLowerCase().includes('revenue') ? iconMap.revenue : (metric.toLowerCase().includes('churn') ? iconMap.churn : iconMap.default);
        return (
          <div key={metric} className="metric-card">
            <div className="metric-icon">
              <Icon />
            </div>
            <div className="metric-info">
              <h4>{metric}</h4>
              <p>{Math.floor(Math.random() * 50000).toLocaleString()}</p>
              <span>{`+${(Math.random() * 10).toFixed(1)}%`}</span>
            </div>
          </div>
        )
      })}
    </div>
  );
};

export default MetricsDisplay;