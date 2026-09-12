import React from 'react';
import clsx from 'clsx';

const PriorityBadge = ({ priority }) => {
  let color = 'bg-gray-500 text-white';
  const p = priority?.toLowerCase();
  if (p === 'critical') color = 'bg-red-600 text-white';
  else if (p === 'high') color = 'bg-orange-500 text-white';
  else if (p === 'medium') color = 'bg-yellow-400 text-gray-900';
  else if (p === 'low') color = 'bg-green-500 text-white';

  return (
    <span className={clsx("uppercase rounded px-2 py-0.5 text-xs font-bold inline-block", color)}>
      {priority}
    </span>
  );
};

export default PriorityBadge;
