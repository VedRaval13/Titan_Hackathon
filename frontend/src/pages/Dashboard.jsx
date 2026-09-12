import React from 'react';
import { useTasks } from '../hooks/useTasks';
import { useEmployees } from '../hooks/useEmployees';
import PriorityBadge from '../components/PriorityBadge';
import WorkloadBar from '../components/WorkloadBar';
import { Briefcase, Users, CheckCircle, Activity } from 'lucide-react';

const Dashboard = () => {
  const { data: tasks = [] } = useTasks();
  const { data: employees = [] } = useEmployees();

  const openTasks = tasks.filter(t => t.status === 'open' || t.status === 'in_progress').length;
  const availableEmployees = employees.filter(e => e.availability_status === 'available').length;
  const avgWorkload = employees.length
    ? (employees.reduce((acc, e) => acc + (e.current_workload_score || 0), 0) / employees.length).toFixed(1)
    : 0;

  const recentTasks = [...tasks].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10);
  const sortedEmployees = [...employees].sort((a, b) => (b.current_workload_score || 0) - (a.current_workload_score || 0));

  const stats = [
    { label: 'Total Tasks', value: tasks.length, icon: Briefcase, color: 'text-blue-600', bg: 'bg-blue-100' },
    { label: 'Open Tasks', value: openTasks, icon: CheckCircle, color: 'text-orange-600', bg: 'bg-orange-100' },
    { label: 'Available Employees', value: availableEmployees, icon: Users, color: 'text-green-600', bg: 'bg-green-100' },
    { label: 'Avg Workload', value: `${avgWorkload}/10`, icon: Activity, color: 'text-purple-600', bg: 'bg-purple-100' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((s, idx) => (
          <div key={idx} className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex items-center">
            <div className={`p-4 rounded-full mr-4 ${s.bg} ${s.color}`}>
              <s.icon size={24} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{s.label}</p>
              <p className="text-2xl font-bold text-gray-900">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        <div className="lg:w-3/5 bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Recent Tasks</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-200 text-sm text-gray-500">
                  <th className="pb-3 font-medium">Title</th>
                  <th className="pb-3 font-medium">Priority</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Assigned To</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                {recentTasks.map(t => {
                  const emp = employees.find(e => e.id === t.assigned_employee_id);
                  return (
                    <tr key={t.id} className="border-b border-gray-100 hover:bg-slate-50">
                      <td className="py-3 font-medium text-gray-800">{t.title}</td>
                      <td className="py-3"><PriorityBadge priority={t.priority} /></td>
                      <td className="py-3">
                        <span className="capitalize text-gray-600">{t.status?.replace('_', ' ')}</span>
                      </td>
                      <td className="py-3 text-gray-600">{emp ? emp.name : 'Unassigned'}</td>
                    </tr>
                  );
                })}
                {recentTasks.length === 0 && (
                  <tr>
                    <td colSpan="4" className="py-4 text-center text-gray-500">No tasks found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="lg:w-2/5 bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Workload Overview</h2>
          <div className="space-y-4">
            {sortedEmployees.map(e => (
              <div key={e.id}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium text-gray-800">{e.name}</span>
                  <span className="text-gray-500">{(e.current_workload_score || 0).toFixed(1)}/10</span>
                </div>
                <WorkloadBar value={e.current_workload_score || 0} />
              </div>
            ))}
            {sortedEmployees.length === 0 && (
              <div className="text-center text-gray-500 py-4">No employees found.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
