import React, { useState, useEffect, useRef } from 'react';
import { useEmployees, useCreateEmployee, useEmployeeHistory, useSyncEmployeesFromJira } from '../hooks/useEmployees';
import { useJiraStatus } from '../hooks/useTasks';
import SkillBadge from '../components/SkillBadge';
import WorkloadBar from '../components/WorkloadBar';
import { Plus, X, User, RefreshCw } from 'lucide-react';
import clsx from 'clsx';

const EmployeeCard = ({ employee, onClick }) => {
  const statusColors = {
    available: 'bg-green-100 text-green-800',
    partial: 'bg-yellow-100 text-yellow-800',
    busy: 'bg-orange-100 text-orange-800',
    unavailable: 'bg-red-100 text-red-800'
  };

  return (
    <div
      onClick={() => onClick(employee)}
      className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-500 mr-3">
            <User size={20} />
          </div>
          <div>
            <h3 className="font-bold text-gray-900">{employee.name}</h3>
            <p className="text-xs text-gray-500">
              {employee.department || 'No department'}
              {employee.jira_account_id && (
                <span className="ml-2 text-blue-600 font-medium">• Jira</span>
              )}
            </p>
          </div>
        </div>
        <span className={clsx("px-2 py-1 rounded text-xs font-medium capitalize", statusColors[employee.availability_status] || 'bg-gray-100')}>
          {employee.availability_status}
        </span>
      </div>

      <div className="mb-3">
        <p className="text-xs text-gray-500 mb-1">Experience: {employee.experience_years} years</p>
      </div>

      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1 text-gray-600">
          <span>Workload</span>
          <span>{(employee.current_workload_score || 0).toFixed(1)}/10</span>
        </div>
        <WorkloadBar value={employee.current_workload_score || 0} />
      </div>

      <div>
        <p className="text-xs font-medium text-gray-700 mb-2">Skills</p>
        <div className="flex flex-wrap">
          {employee.skills?.slice(0, 4).map(s => <SkillBadge key={s} skill={s} />)}
          {employee.skills?.length > 4 && <span className="text-xs text-gray-500 ml-1">+{employee.skills.length - 4}</span>}
        </div>
      </div>
    </div>
  );
};

const EmployeeDetail = ({ employee, onClose }) => {
  const { data: history = [], isLoading } = useEmployeeHistory(employee.id);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-gray-600">
          <X size={20} />
        </button>
        <h3 className="text-xl font-bold text-gray-900 mb-2">{employee.name}</h3>
        <p className="text-gray-500 mb-6">{employee.email} • {employee.department || 'N/A'} • {employee.experience_years} yrs exp</p>

        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Skills</p>
          <div className="flex flex-wrap gap-1">
            {employee.skills?.map(s => <SkillBadge key={s} skill={s} />)}
          </div>
        </div>

        <h4 className="font-bold text-gray-800 mb-3">Assignment History</h4>
        {isLoading ? (
          <p className="text-sm text-gray-500">Loading history...</p>
        ) : history.length === 0 ? (
          <p className="text-sm text-gray-500">No past assignments.</p>
        ) : (
          <div className="space-y-3">
            {history.map(a => (
              <div key={a.id} className="p-3 bg-slate-50 border border-slate-100 rounded-lg text-sm text-gray-600 flex justify-between">
                <span>Task #{a.task_id}</span>
                <span className="capitalize">{a.status}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const Employees = () => {
  const { data: employees = [], isLoading } = useEmployees();
  const createEmployeeMutation = useCreateEmployee();
  const syncJiraMutation = useSyncEmployeesFromJira();
  const { data: jiraStatus } = useJiraStatus();
  const hasSynced = useRef(false);

  const [showModal, setShowModal] = useState(false);
  const [selectedEmp, setSelectedEmp] = useState(null);
  const [syncResult, setSyncResult] = useState(null);

  const [formData, setFormData] = useState({
    name: '', email: '', department: '', skills: '', experience_years: 1, availability_status: 'available'
  });

  // Auto-sync from Jira on page load
  useEffect(() => {
    const jiraConnected = jiraStatus?.configured && jiraStatus?.connected;
    if (jiraConnected && !hasSynced.current) {
      hasSynced.current = true;
      syncJiraMutation.mutate(undefined, {
        onSuccess: (data) => setSyncResult(data),
      });
    }
  }, [jiraStatus]);

  const handleSyncJira = () => {
    setSyncResult(null);
    syncJiraMutation.mutate(undefined, {
      onSuccess: (data) => setSyncResult(data),
      onError: (err) => setSyncResult({ status: 'error', message: err.response?.data?.detail || err.message }),
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = {
      ...formData,
      skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean),
      experience_years: parseInt(formData.experience_years, 10)
    };
    createEmployeeMutation.mutate(data, {
      onSuccess: () => {
        setShowModal(false);
        setFormData({ name: '', email: '', department: '', skills: '', experience_years: 1, availability_status: 'available' });
      }
    });
  };

  const jiraConnected = jiraStatus?.configured && jiraStatus?.connected;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
        <div className="flex gap-3">
          <button
            onClick={handleSyncJira}
            disabled={syncJiraMutation.isPending || !jiraConnected}
            className={`rounded-lg px-4 py-2 font-medium flex items-center transition-colors text-sm ${
              jiraConnected
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
            title={jiraConnected ? 'Pull team members from Jira' : 'Jira not configured'}
          >
            <RefreshCw size={16} className={`mr-2 ${syncJiraMutation.isPending ? 'animate-spin' : ''}`} />
            {syncJiraMutation.isPending ? 'Syncing...' : 'Sync Jira'}
          </button>
          <button
            onClick={() => setShowModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium flex items-center transition-colors text-sm"
          >
            <Plus size={18} className="mr-2" />
            Add Employee
          </button>
        </div>
      </div>

      {/* Sync Result */}
      {syncResult && syncResult.status !== 'error' && (syncResult.created > 0 || syncResult.linked > 0) && (
        <div className="text-sm px-4 py-3 rounded-lg bg-blue-50 text-blue-700 border border-blue-200">
          Synced! {syncResult.created} new employees imported, {syncResult.linked} linked to Jira ({syncResult.total_jira_users} Jira users total)
          <button onClick={() => setSyncResult(null)} className="ml-3 font-bold">×</button>
        </div>
      )}

      {isLoading ? (
        <div className="text-center py-10 text-gray-500">Loading employees...</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {employees.map(emp => (
            <EmployeeCard key={emp.id} employee={emp} onClick={setSelectedEmp} />
          ))}
          {employees.length === 0 && (
            <div className="col-span-3 text-center py-10 text-gray-500">No employees found. Add one to get started.</div>
          )}
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add Employee</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input required type="text" className="w-full border border-slate-300 rounded-lg p-2" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input required type="email" className="w-full border border-slate-300 rounded-lg p-2" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                <input required type="text" className="w-full border border-slate-300 rounded-lg p-2" value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma separated)</label>
                <input required type="text" className="w-full border border-slate-300 rounded-lg p-2" value={formData.skills} onChange={e => setFormData({...formData, skills: e.target.value})} />
              </div>
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Exp Years</label>
                  <input required type="number" min="0" className="w-full border border-slate-300 rounded-lg p-2" value={formData.experience_years} onChange={e => setFormData({...formData, experience_years: e.target.value})} />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Availability</label>
                  <select className="w-full border border-slate-300 rounded-lg p-2" value={formData.availability_status} onChange={e => setFormData({...formData, availability_status: e.target.value})}>
                    <option value="available">Available</option>
                    <option value="partial">Partial</option>
                    <option value="busy">Busy</option>
                    <option value="unavailable">Unavailable</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 border border-slate-300 rounded-lg text-gray-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={createEmployeeMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {createEmployeeMutation.isPending ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {selectedEmp && <EmployeeDetail employee={selectedEmp} onClose={() => setSelectedEmp(null)} />}
    </div>
  );
};

export default Employees;
