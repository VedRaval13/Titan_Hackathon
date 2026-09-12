import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTasks } from '../hooks/useTasks';
import { useGenerateRecommendations, useRecommendations, useApproveRecommendation, useOverrideRecommendation } from '../hooks/useRecommendations';
import RecommendCard from '../components/RecommendCard';
import ConfirmModal from '../components/ConfirmModal';

const Recommendations = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTaskId = searchParams.get('taskId');
  
  const [selectedTask, setSelectedTask] = useState(initialTaskId || '');
  const { data: tasks = [] } = useTasks();
  const generateMutation = useGenerateRecommendations();
  const approveMutation = useApproveRecommendation();
  const overrideMutation = useOverrideRecommendation();
  
  const { data: recommendations = [], isLoading: isRecsLoading } = useRecommendations(selectedTask);
  
  const [confirmState, setConfirmState] = useState({ isOpen: false, type: '', recId: null });
  const [overrideReason, setOverrideReason] = useState('');
  
  const openTasks = tasks.filter(t => !t.assigned_to && t.status !== 'completed');

  useEffect(() => {
    if (initialTaskId) {
      setSelectedTask(initialTaskId);
    }
  }, [initialTaskId]);

  const handleGenerate = () => {
    if (selectedTask) {
      generateMutation.mutate(selectedTask);
    }
  };

  const handleApprove = (recId) => {
    approveMutation.mutate(recId, {
      onSuccess: () => {
        alert('Recommendation approved successfully!');
        setConfirmState({ isOpen: false, type: '', recId: null });
      }
    });
  };

  const handleOverride = (recId) => {
    overrideMutation.mutate({ id: recId, data: { reason: overrideReason } }, {
      onSuccess: () => {
        alert('Recommendation overridden successfully!');
        setConfirmState({ isOpen: false, type: '', recId: null });
        setOverrideReason('');
      }
    });
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
      
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Task for Assignment</label>
        <div className="flex gap-4">
          <select 
            className="flex-1 border border-slate-300 rounded-lg p-2 bg-white"
            value={selectedTask}
            onChange={e => {
              setSelectedTask(e.target.value);
              setSearchParams({ taskId: e.target.value });
            }}
          >
            <option value="">-- Select an unassigned task --</option>
            {openTasks.map(t => (
              <option key={t.id} value={t.id}>{t.title} ({t.priority})</option>
            ))}
          </select>
          <button 
            onClick={handleGenerate}
            disabled={!selectedTask || generateMutation.isPending}
            className="bg-primary-500 hover:bg-primary-600 text-white rounded-lg px-6 py-2 font-medium transition-colors disabled:opacity-50"
          >
            {generateMutation.isPending ? 'Generating...' : 'Generate Recommendations'}
          </button>
        </div>
      </div>

      {isRecsLoading ? (
        <div className="text-center py-10 text-gray-500">Loading recommendations...</div>
      ) : recommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {recommendations.map((rec, idx) => (
            <RecommendCard 
              key={rec.id} 
              recommendation={{...rec, rank: idx + 1}} 
              onApprove={() => setConfirmState({ isOpen: true, type: 'approve', recId: rec.id })}
              onOverride={() => setConfirmState({ isOpen: true, type: 'override', recId: rec.id })}
            />
          ))}
        </div>
      ) : selectedTask ? (
        <div className="text-center py-10 text-gray-500">Click generate to get recommendations for this task.</div>
      ) : null}

      <ConfirmModal 
        isOpen={confirmState.isOpen && confirmState.type === 'approve'}
        onClose={() => setConfirmState({ isOpen: false, type: '', recId: null })}
        onConfirm={() => handleApprove(confirmState.recId)}
        title="Approve Assignment"
        message="Are you sure you want to assign this task to the selected employee?"
        confirmText="Approve Assignment"
      />

      {confirmState.isOpen && confirmState.type === 'override' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Override Recommendation</h3>
            <p className="text-sm text-gray-600 mb-4">Please provide a reason for overriding this recommendation.</p>
            <textarea 
              className="w-full border border-slate-300 rounded-lg p-2 h-24 mb-6"
              placeholder="Reason for override..."
              value={overrideReason}
              onChange={e => setOverrideReason(e.target.value)}
            ></textarea>
            <div className="flex justify-end gap-3">
              <button onClick={() => setConfirmState({ isOpen: false, type: '', recId: null })} className="px-4 py-2 rounded-lg font-medium border border-slate-300 hover:bg-slate-50">Cancel</button>
              <button 
                onClick={() => handleOverride(confirmState.recId)}
                disabled={!overrideReason.trim()}
                className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium disabled:opacity-50"
              >
                Submit Override
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
