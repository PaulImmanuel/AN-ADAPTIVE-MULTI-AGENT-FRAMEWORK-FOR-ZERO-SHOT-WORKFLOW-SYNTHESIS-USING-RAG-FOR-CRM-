import React from 'react';

const DataTable = ({ columns }) => {
  const generateFakeData = (column, index) => {
    const colLower = column.toLowerCase();
    if (colLower.includes('email')) return `contact${index}@example.com`;
    if (colLower.includes('name')) return `Person ${index}`;
    if (colLower.includes('company')) return `Company ${String.fromCharCode(65 + index)}`;
    if (colLower.includes('phone')) return `555-010${index}`;
    if (colLower.includes('status')) return ['New', 'Contacted', 'Qualified'][index % 3];
    return `Value ${index}`;
  };

  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => <th key={col}>{col}</th>)}
          </tr>
        </thead>
        <tbody>
          {Array(8).fill(0).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((col) => <td key={col}>{generateFakeData(col, rowIndex + 1)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;