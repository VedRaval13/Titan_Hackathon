import React from 'react';

const RecommendCard = ({ recommendation, onApprove, onOverride }) => {
  const { employee_name, match_score, reason, breakdown, rank } = recommendation;
  
  const rankColors = {
    1: 'bg-yellow-400 text-yellow-900', // Gold
    2: 'bg-gray-300 text-gray-800',     // Silver
    3: 'bg-orange-300 text-orange-900'  // Bronze
  };
  
  const rankLabels = {
    1: '#1 Best Match',
    2: '#2 Good Match',
    3: '#3 Suitable'
  };

  const badgeClass = rankColors[rank] || 'bg-blue-100 text-blue-800';
  const badgeLabel = rankLabels[rank] || `#${rank} Match`;

  return (
    <div className="bg-white shadow-lg rounded-xl p-6 border border-slate-200">
      <div className="flex justify-between items-start mb-4">
        <div>
          <span className={`inline-block px-2 py-1 rounded text-xs font-bold mb-2 ${badgeClass}`}>
            {badgeLabel}
          </span>
          <h3 className="text-xl font-bold text-gray-800">{employee_name}</h3>
        </div>
        <div className="flex items-center justify-center w-16 h-16 rounded-full border-4 border-primary-500">
          <span className="text-lg font-bold text-primary-900">{Math.round(match_score * 100)}%</span>
        </div>
      </div>
      
      <div className="mb-4">
        <p className="text-sm text-gray-600 italic">"{reason}"</p>
      </div>

      {breakdown && (
        <div className="space-y-2 mb-6">
          {Object.entries(breakdown).slice(0, 5).map(([key, val]) => (
            <div key={key} className="flex items-center text-sm">
              <span className="w-1/3 truncate text-gray-600 capitalize">{key.replace('_', ' ')}</span>
              <div className="w-1/2 bg-gray-200 rounded-full h-1.5 ml-2">
                <div 
                  className="bg-primary-300 h-1.5 rounded-full" 
                  style={{ width: `${Math.min(Math.round(val * 100), 100)}%` }}
                ></div>
              </div>
              <span className="ml-2 text-xs text-gray-500 w-10 text-right">{Math.round(val * 100)}%</span>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-3">
        <button 
          onClick={onApprove}
          className="flex-1 bg-success hover:bg-green-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
        >
          Approve
        </button>
        <button 
          onClick={onOverride}
          className="flex-1 border border-slate-300 hover:bg-slate-50 text-gray-700 rounded-lg px-4 py-2 font-medium transition-colors"
        >
          Override
        </button>
      </div>
    </div>
  );
};

export default RecommendCard;
