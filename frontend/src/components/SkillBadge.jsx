import React from 'react';
import clsx from 'clsx';

const getSkillColor = (skill) => {
  const lower = skill.toLowerCase();
  if (['python', 'java', 'c++'].includes(lower)) return 'bg-blue-100 text-blue-800';
  if (['react', 'vue', 'angular', 'css', 'html'].includes(lower)) return 'bg-green-100 text-green-800';
  if (['docker', 'k8s', 'aws', 'devops', 'kubernetes'].includes(lower)) return 'bg-purple-100 text-purple-800';
  if (['sql', 'database', 'mongodb'].includes(lower)) return 'bg-orange-100 text-orange-800';
  return 'bg-gray-100 text-gray-800';
};

const SkillBadge = ({ skill }) => {
  return (
    <span className={clsx("rounded-full px-2 py-0.5 text-xs font-medium mr-1 mb-1 inline-block", getSkillColor(skill))}>
      {skill}
    </span>
  );
};

export default SkillBadge;
