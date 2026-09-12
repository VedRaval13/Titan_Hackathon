import React, { useState, useEffect, useRef } from 'react';
import { useTasks, useAnalyzeTask, useCreateTask, useUpdateTask, useSyncFromJira, useJiraStatus } from '../hooks/useTasks';
import { useEmployees } from '../hooks/useEmployees';
import PriorityBadge from '../components/PriorityBadge';
import SkillBadge from '../components/SkillBadge';
import { useNavigate } from 'react-router-dom';
import { Search, Plus, X, Brain, RefreshCw, ExternalLink } from 'lucide-react';

const Tasks = () => {
  const { data: tasks = [], isLoading } = useTasks();
  const { data: employees = [] } = useEmployees();
  const { data: jiraStatus } = useJiraStatus();
  const analyzeTaskMutation = useAnalyzeTask();
  const createTaskMutation = useCreateTask();
  const updateTaskMutation = useUpdateTask();
  const syncJiraMutation = useSyncFromJira();
  const navigate = useNavigate();
  const hasSynced = useRef(false);

  // Auto-sync from Jira on page load and every 30 seconds
  useEffect(() => {
    const jiraConnected = jiraStatus?.configured && jiraStatus?.connected;
    if (jiraConnected && !hasSynced.current) {
      hasSynced.current = true;
      syncJiraMutation.mutate();
    }

    if (jiraConnected) {
      const interval = setInterval(() => {
        syncJiraMutation.mutate();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [jiraStatus]);

  const [selectedTask, setSelectedTask] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [syncResult, setSyncResult] = useState(null);
  const [newTask, setNewTask] = useState({
    title: '', description: '', priority: 'medium', task_type: 'backend',
    required_skills: '', push_to_jira: false,
  });

  const filteredTasks = tasks.filter(t =>
    t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (t.description || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleAnalyze = (id) => {
    analyzeTaskMutation.mutate(id);
  };

  const handleCreateTask = (e) => {
    e.preventDefault();
    const data = {
      ...newTask,
      required_skills: newTask.required_skills
        ? newTask.required_skills.split(',').map(s => s.trim()).filter(Boolean)
        : [],
    };
    createTaskMutation.mutate(data, {
      onSuccess: () => {
        setShowCreateModal(false);
        setNewTask({ title: '', description: '', priority: 'medium', task_type: 'backend', required_skills: '', push_to_jira: false });
      }
    });
  };

  const handleSyncJira = () => {
    setSyncResult(null);
    syncJiraMutation.mutate(undefined, {
      onSuccess: (data) => setSyncResult(data),
      onError: (err) => setSyncResult({ status: 'error', message: err.response?.data?.detail || err.message }),
    });
  };

  const jiraConnected = jiraStatus?.configured && jiraStatus?.connected;

  return (
    <div className="space-y-6 relative h-full">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
        <div className="flex gap-3">
          {/* Jira Sync Button */}
          <button
            onClick={handleSyncJira}
            disabled={syncJiraMutation.isPending}
            className={`rounded-lg px-4 py-2 font-medium flex items-center transition-colors text-sm ${
              jiraConnected
                ? 'bg-blue-500 hover:bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
            title={jiraConnected ? 'Pull tasks from Jira' : 'Jira not configured - set credentials in .env'}
          >
            <RefreshCw size={16} className={`mr-2 ${syncJiraMutation.isPending ? 'animate-spin' : ''}`} />
            {syncJiraMutation.isPending ? 'Syncing...' : 'Sync Jira'}
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium flex items-center transition-colors text-sm"
          >
            <Plus size={18} className="mr-2" />
            Add Task
          </button>
        </div>
      </div>

      {/* Jira Status Banner */}
      {jiraStatus && (
        <div className={`text-xs px-4 py-2 rounded-lg flex items-center justify-between ${
          jiraConnected ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
        }`}>
          <span>
            {jiraConnected
              ? `Jira connected as ${jiraStatus.user} | Project: ${jiraStatus.project_key}`
              : 'Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN in .env to enable sync.'}
          </span>
          {jiraConnected && (
            <a href={jiraStatus.jira_url} target="_blank" rel="noopener noreferrer" className="flex items-center hover:underline">
              Open Jira <ExternalLink size={12} className="ml-1" />
            </a>
          )}
        </div>
      )}

      {/* Sync Result */}
      {syncResult && (
        <div className={`text-sm px-4 py-3 rounded-lg ${
          syncResult.status === 'error' ? 'bg-red-50 text-red-700 border border-red-200' : 'bg-blue-50 text-blue-700 border border-blue-200'
        }`}>
          {syncResult.status === 'error'
            ? `Sync failed: ${syncResult.message}`
            : `Synced! ${syncResult.created} new tasks imported, ${syncResult.updated} updated (${syncResult.total_jira_issues} total Jira issues)`}
          <button onClick={() => setSyncResult(null)} className="ml-3 font-bold">x</button>
        </div>
      )}

      <div className="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex items-center">
        <Search className="text-gray-400 mr-2" size={20} />
        <input
          type="text"
          placeholder="Search tasks..."
          className="flex-1 outline-none text-sm"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="flex gap-6 relative">
        <div className={`transition-all duration-300 ${selectedTask ? 'w-2/3' : 'w-full'} bg-white rounded-xl shadow-sm border border-slate-200 p-6 overflow-x-auto`}>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-200 text-sm text-gray-500">
                <th className="pb-3 font-medium">Title</th>
                <th className="pb-3 font-medium">Jira</th>
                <th className="pb-3 font-medium">Priority</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Skills</th>
                <th className="pb-3 font-medium">Assigned To</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {isLoading ? (
                <tr><td colSpan="6" className="py-4 text-center text-gray-500">Loading tasks...</td></tr>
              ) : filteredTasks.map(t => {
                const emp = employees.find(e => e.id === t.assigned_employee_id);
                return (
                  <tr
                    key={t.id}
                    className={`border-b border-gray-100 hover:bg-slate-50 cursor-pointer ${selectedTask?.id === t.id ? 'bg-blue-50' : ''}`}
                    onClick={() => setSelectedTask(t)}
                  >
                    <td className="py-3 font-medium text-gray-800">{t.title}</td>
                    <td className="py-3">
                      {t.jira_issue_key ? (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded font-mono">
                          {t.jira_issue_key}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="py-3"><PriorityBadge priority={t.priority} /></td>
                    <td className="py-3 capitalize text-gray-600">{t.status?.replace('_', ' ')}</td>
                    <td className="py-3">
                      {t.required_skills?.slice(0, 2).map(s => <SkillBadge key={s} skill={s} />)}
                      {t.required_skills?.length > 2 && <span className="text-xs text-gray-500">+{t.required_skills.length - 2}</span>}
                    </td>
                    <td className="py-3 text-gray-600">{emp ? emp.name : 'Unassigned'}</td>
                  </tr>
                );
              })}
              {!isLoading && filteredTasks.length === 0 && (
                <tr><td colSpan="6" className="py-4 text-center text-gray-500">No tasks found.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        {selectedTask && (
          <div className="w-1/3 bg-white rounded-xl shadow-sm border border-slate-200 p-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold text-gray-900">{selectedTask.title}</h2>
              <button onClick={() => { setSelectedTask(null); setEditingTask(null); }} className="text-gray-400 hover:text-gray-600">
                <X size={20} />
              </button>
            </div>

            {selectedTask.jira_issue_key && (
              <div className="mb-3">
                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded font-mono">
                  {selectedTask.jira_issue_key}
                </span>
                <span className="text-xs text-gray-400 ml-2">Linked to Jira</span>
              </div>
            )}

            {/* EDIT MODE */}
            {editingTask ? (
              <form
                className="space-y-3 text-sm"
                onSubmit={(e) => {
                  e.preventDefault();
                  updateTaskMutation.mutate(
                    { id: selectedTask.id, data: editingTask },
                    {
                      onSuccess: () => {
                        setEditingTask(null);
                        setSelectedTask(null);
                      },
                    }
                  );
                }}
              >
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Title</label>
                  <input
                    type="text"
                    className="w-full border border-slate-300 rounded-lg p-2"
                    value={editingTask.title || ''}
                    onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block font-medium text-gray-700 mb-1">Description</label>
                  <textarea
                    className="w-full border border-slate-300 rounded-lg p-2 h-20"
                    value={editingTask.description || ''}
                    onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                  ></textarea>
                </div>
                <div className="flex gap-3">
                  <div className="flex-1">
                    <label className="block font-medium text-gray-700 mb-1">Priority</label>
                    <select
                      className="w-full border border-slate-300 rounded-lg p-2"
                      value={editingTask.priority || 'medium'}
                      onChange={(e) => setEditingTask({ ...editingTask, priority: e.target.value })}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  <div className="flex-1">
                    <label className="block font-medium text-gray-700 mb-1">Status</label>
                    <select
                      className="w-full border border-slate-300 rounded-lg p-2"
                      value={editingTask.status || 'open'}
                      onChange={(e) => setEditingTask({ ...editingTask, status: e.target.value })}
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="done">Done</option>
                    </select>
                  </div>
                </div>
                {selectedTask.jira_issue_key && (
                  <p className="text-xs text-blue-600 bg-blue-50 p-2 rounded">
                    Changes will sync to Jira ({selectedTask.jira_issue_key})
                  </p>
                )}
                <div className="flex gap-2 pt-2">
                  <button
                    type="submit"
                    disabled={updateTaskMutation.isPending}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium disabled:opacity-50"
                  >
                    {updateTaskMutation.isPending ? 'Saving...' : 'Save & Sync'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingTask(null)}
                    className="px-4 py-2 border border-slate-300 rounded-lg text-gray-700 hover:bg-slate-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              /* VIEW MODE */
              <div className="space-y-4 text-sm text-gray-700">
                <p>{selectedTask.description || 'No description.'}</p>

                <div className="flex gap-2">
                  <span className="text-xs font-medium text-gray-500">Priority:</span>
                  <PriorityBadge priority={selectedTask.priority} />
                  <span className="text-xs font-medium text-gray-500 ml-3">Status:</span>
                  <span className="text-xs capitalize bg-gray-100 px-2 py-0.5 rounded">{selectedTask.status?.replace('_', ' ')}</span>
                </div>

                {selectedTask.required_skills?.length > 0 && (
                  <div>
                    <span className="font-medium block mb-1">Skills:</span>
                    {selectedTask.required_skills.map(s => <SkillBadge key={s} skill={s} />)}
                  </div>
                )}

                {/* Edit Button */}
                <button
                  onClick={() =>
                    setEditingTask({
                      title: selectedTask.title,
                      description: selectedTask.description || '',
                      priority: selectedTask.priority,
                      status: selectedTask.status,
                    })
                  }
                  className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg px-4 py-2 font-medium transition-colors"
                >
                  Edit Task {selectedTask.jira_issue_key ? '(syncs to Jira)' : ''}
                </button>

                <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                  <h3 className="font-bold text-gray-900 mb-2 flex items-center">
                    <Brain size={16} className="mr-2 text-blue-500" />
                    AI Analysis
                  </h3>
                  {selectedTask.ai_analysis ? (
                    <div className="space-y-2">
                      <p><span className="font-medium">Estimated Hours:</span> {selectedTask.ai_analysis.estimated_hours}</p>
                      <p><span className="font-medium">Difficulty:</span> {selectedTask.ai_analysis.difficulty}</p>
                      <p><span className="font-medium">Complexity:</span> {selectedTask.ai_analysis.complexity_notes}</p>
                      <div>
                        <span className="font-medium block mb-1">Required Skills:</span>
                        {selectedTask.required_skills?.map(s => <SkillBadge key={s} skill={s} />)}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-gray-500 mb-3">No AI analysis available yet.</p>
                      <button
                        onClick={() => handleAnalyze(selectedTask.id)}
                        disabled={analyzeTaskMutation.isPending}
                        className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2 font-medium transition-colors disabled:opacity-50"
                      >
                        {analyzeTaskMutation.isPending ? 'Analyzing...' : 'Analyze with AI'}
                      </button>
                    </div>
                  )}
                </div>

                {!selectedTask.assigned_employee_id && (
                  <button
                    onClick={() => navigate(`/recommendations?taskId=${selectedTask.id}`)}
                    className="w-full bg-amber-500 hover:bg-amber-600 text-white rounded-lg px-4 py-2 font-medium transition-colors"
                  >
                    Get Recommendations
                  </button>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Create Task Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Add New Task</h3>
            <form onSubmit={handleCreateTask} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input required type="text" className="w-full border border-slate-300 rounded-lg p-2" value={newTask.title} onChange={e => setNewTask({...newTask, title: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea required className="w-full border border-slate-300 rounded-lg p-2 h-24" value={newTask.description} onChange={e => setNewTask({...newTask, description: e.target.value})}></textarea>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Required Skills (comma separated)</label>
                <input type="text" className="w-full border border-slate-300 rounded-lg p-2" placeholder="python, react, sql" value={newTask.required_skills} onChange={e => setNewTask({...newTask, required_skills: e.target.value})} />
              </div>
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select className="w-full border border-slate-300 rounded-lg p-2" value={newTask.priority} onChange={e => setNewTask({...newTask, priority: e.target.value})}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                  <select className="w-full border border-slate-300 rounded-lg p-2" value={newTask.task_type} onChange={e => setNewTask({...newTask, task_type: e.target.value})}>
                    <option value="backend">Backend</option>
                    <option value="frontend">Frontend</option>
                    <option value="devops">DevOps</option>
                    <option value="qa">QA</option>
                    <option value="design">Design</option>
                    <option value="data">Data</option>
                  </select>
                </div>
              </div>

              {/* Push to Jira Toggle */}
              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <input
                  type="checkbox"
                  id="pushToJira"
                  checked={newTask.push_to_jira}
                  onChange={e => setNewTask({...newTask, push_to_jira: e.target.checked})}
                  className="w-4 h-4 text-blue-600 rounded"
                  disabled={!jiraConnected}
                />
                <label htmlFor="pushToJira" className={`text-sm font-medium ${jiraConnected ? 'text-blue-700' : 'text-gray-400'}`}>
                  Also create in Jira
                  {!jiraConnected && <span className="text-xs ml-1">(not configured)</span>}
                </label>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 border border-slate-300 rounded-lg text-gray-700 hover:bg-slate-50">Cancel</button>
                <button type="submit" disabled={createTaskMutation.isPending} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50">
                  {createTaskMutation.isPending ? 'Saving...' : 'Save Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tasks;
