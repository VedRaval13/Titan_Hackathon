import React, { useState } from 'react';
import { usePreviewOptimization, useApplyOptimization } from '../hooks/useOptimizer';
import ConfirmModal from '../components/ConfirmModal';
import WorkloadBar from '../components/WorkloadBar';

const Optimizer = () => {
  const previewMutation = usePreviewOptimization();
  const applyMutation = useApplyOptimization();
  const [previewData, setPreviewData] = useState(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);

  const handlePreview = () => {
    previewMutation.mutate(undefined, {
      onSuccess: (data) => {
        setPreviewData(data);
      }
    });
  };

  const handleApply = () => {
    if (previewData) {
      applyMutation.mutate(previewData, {
        onSuccess: () => {
          setPreviewData(null);
          alert('Optimization applied successfully!');
        }
      });
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 mb-1">Workload Optimizer</h1>
          <p className="text-gray-500 text-sm">Run the global optimization solver to balance team workload while maximizing skill matches.</p>
        </div>
        <button 
          onClick={handlePreview}
          disabled={previewMutation.isPending}
          className="bg-primary-500 hover:bg-primary-600 text-white rounded-lg px-6 py-2 font-medium transition-colors disabled:opacity-50"
        >
          {previewMutation.isPending ? 'Running Solver...' : 'Preview Optimization'}
        </button>
      </div>

      {previewData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-gray-700 mb-2">Solver Status</h3>
              <p className={`text-lg font-bold capitalize ${previewData.status === 'optimal' ? 'text-green-600' : 'text-orange-500'}`}>
                {previewData.status}
              </p>
              {previewData.relaxed && (
                <div className="mt-2 text-xs bg-yellow-100 text-yellow-800 p-2 rounded">
                  Warning: Constraints were relaxed to find a feasible solution.
                </div>
              )}
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-gray-700 mb-2">Tasks Assessed</h3>
              <p className="text-3xl font-bold text-gray-900">{previewData.metrics?.total_tasks || 0}</p>
            </div>
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <h3 className="font-bold text-gray-700 mb-2">Max Workload After</h3>
              <p className="text-3xl font-bold text-gray-900">{previewData.metrics?.max_workload_after || 0}/10</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">Proposed Assignments</h2>
              <button 
                onClick={() => setIsConfirmOpen(true)}
                className="bg-success hover:bg-green-700 text-white rounded-lg px-4 py-2 font-medium transition-colors"
              >
                Apply Optimization
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-gray-200 text-sm text-gray-500">
                    <th className="pb-3 font-medium">Task</th>
                    <th className="pb-3 font-medium">Assigned Employee</th>
                    <th className="pb-3 font-medium">Estimated Hours</th>
                  </tr>
                </thead>
                <tbody className="text-sm">
                  {previewData.assignments?.map((a, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-slate-50">
                      <td className="py-3 font-medium text-gray-800">{a.task_title || a.task_id}</td>
                      <td className="py-3 text-gray-600">{a.employee_name || a.employee_id}</td>
                      <td className="py-3 text-gray-600">{a.estimated_hours || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      <ConfirmModal 
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleApply}
        title="Apply Optimization"
        message="This will immediately apply the proposed assignments and update the database. Are you sure you want to proceed?"
        confirmText="Apply Assignments"
      />
    </div>
  );
};

export default Optimizer;
