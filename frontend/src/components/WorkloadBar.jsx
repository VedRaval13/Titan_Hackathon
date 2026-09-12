import React from 'react';
import clsx from 'clsx';

const WorkloadBar = ({ value, showLabel = false }) => {
  const pct = Math.min(Math.max((value / 10) * 100, 0), 100);
  let colorClass = 'bg-success';
  if (value >= 4 && value <= 6) colorClass = 'bg-yellow-400';
  else if (value >= 7 && value <= 8) colorClass = 'bg-warning';
  else if (value > 8) colorClass = 'bg-danger';

  return (
    <div className="w-full flex items-center gap-2">
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className={clsx("h-2 rounded-full transition-all duration-300", colorClass)}
          style={{ width: `${pct}%` }}
        ></div>
      </div>
      {showLabel && <span className="text-xs font-medium text-gray-700 w-8">{value}/10</span>}
    </div>
  );
};

export default WorkloadBar;
