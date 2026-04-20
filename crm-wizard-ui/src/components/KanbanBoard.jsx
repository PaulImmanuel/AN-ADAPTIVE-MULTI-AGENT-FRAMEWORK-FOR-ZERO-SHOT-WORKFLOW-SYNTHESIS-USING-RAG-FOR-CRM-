import React from 'react';

const KanbanBoard = ({ stages }) => {
  return (
    <div className="kanban-board">
      {stages.map((stage) => (
        <div key={stage} className="kanban-column">
          <div className="kanban-column-header">
            <h3>{stage}</h3>
            <span>{Math.floor(Math.random() * 5) + 1}</span>
          </div>
          <div className="kanban-column-body">
            {Array(Math.floor(Math.random() * 4) + 1).fill(0).map((_, index) => (
              <div className="kanban-card" key={index}>
                <h4>Lead #{Math.floor(Math.random() * 1000)}</h4>
                <p>A sample task for the {stage} stage.</p>
                <div className="card-footer">Sample Company</div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default KanbanBoard;