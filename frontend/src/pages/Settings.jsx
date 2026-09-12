import React, { useState, useEffect } from 'react';
import { getJiraSettings, saveJiraSettings, testJiraConnection } from '../api/client';
import { Settings as SettingsIcon, CheckCircle, XCircle, Loader2, ExternalLink, Eye, EyeOff } from 'lucide-react';

const Settings = () => {
  const [form, setForm] = useState({
    jira_base_url: '',
    jira_email: '',
    jira_api_token: '',
    jira_project_key: '',
  });
  const [status, setStatus] = useState(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [showToken, setShowToken] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getJiraSettings().then((data) => {
      setForm({
        jira_base_url: data.jira_base_url || '',
        jira_email: data.jira_email || '',
        jira_api_token: data.jira_api_token || '',
        jira_project_key: data.jira_project_key || '',
      });
      setStatus(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setTestResult(null);
    try {
      const result = await saveJiraSettings(form);
      setStatus(result);
      let message = result.connected
        ? `Connected as ${result.user}`
        : 'Settings saved but could not connect. Check your credentials.';
      if (result.data_cleared) {
        message = `Fresh start! Imported ${result.employees_imported} team members and ${result.tasks_imported} tasks from the new Jira server.`;
      }
      setTestResult({ success: result.connected, message });
    } catch (err) {
      setTestResult({ success: false, message: err.response?.data?.detail || 'Failed to save' });
    }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await testJiraConnection();
      setTestResult({
        success: result.connected,
        message: result.connected
          ? `Connected as ${result.user} (${result.email})`
          : `Connection failed: ${result.error}`,
      });
    } catch (err) {
      setTestResult({ success: false, message: err.response?.data?.detail || 'Connection failed' });
    }
    setTesting(false);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-blue-500" size={32} />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <SettingsIcon size={28} className="text-gray-700" />
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
      </div>

      {/* Jira Connection Card */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <img src="https://cdn.worldvectorlogo.com/logos/jira-1.svg" alt="Jira" className="h-8 w-8" />
            <div>
              <h2 className="text-lg font-bold text-gray-900">Jira Integration</h2>
              <p className="text-sm text-gray-500">Connect your Atlassian Jira to sync tasks and team members</p>
            </div>
          </div>
          {status?.connected ? (
            <div className="flex items-center gap-2 bg-green-50 text-green-700 px-3 py-1.5 rounded-lg text-sm font-medium">
              <CheckCircle size={16} />
              Connected
            </div>
          ) : status?.configured ? (
            <div className="flex items-center gap-2 bg-yellow-50 text-yellow-700 px-3 py-1.5 rounded-lg text-sm font-medium">
              <XCircle size={16} />
              Not Connected
            </div>
          ) : (
            <div className="flex items-center gap-2 bg-gray-50 text-gray-500 px-3 py-1.5 rounded-lg text-sm font-medium">
              Not Configured
            </div>
          )}
        </div>

        {status?.connected && (
          <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200 text-sm text-green-800">
            <p>Logged in as <strong>{status.user}</strong></p>
            {form.jira_base_url && (
              <a
                href={form.jira_base_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 mt-1 text-green-600 hover:underline"
              >
                Open Jira <ExternalLink size={12} />
              </a>
            )}
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Jira URL</label>
            <input
              type="url"
              placeholder="https://your-team.atlassian.net"
              className="w-full border border-slate-300 rounded-lg p-2.5 text-sm"
              value={form.jira_base_url}
              onChange={(e) => setForm({ ...form, jira_base_url: e.target.value })}
            />
            <p className="text-xs text-gray-400 mt-1">Your Atlassian cloud URL</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              type="email"
              placeholder="your@email.com"
              className="w-full border border-slate-300 rounded-lg p-2.5 text-sm"
              value={form.jira_email}
              onChange={(e) => setForm({ ...form, jira_email: e.target.value })}
            />
            <p className="text-xs text-gray-400 mt-1">The email associated with your Jira account</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">API Token</label>
            <div className="relative">
              <input
                type={showToken ? 'text' : 'password'}
                placeholder="Your Jira API token"
                className="w-full border border-slate-300 rounded-lg p-2.5 text-sm pr-10"
                value={form.jira_api_token}
                onChange={(e) => setForm({ ...form, jira_api_token: e.target.value })}
              />
              <button
                type="button"
                onClick={() => setShowToken(!showToken)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showToken ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Generate at{' '}
              <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                Atlassian API Tokens
              </a>
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Project Key</label>
            <input
              type="text"
              placeholder="e.g. MP, PROJ, TITAN"
              className="w-full border border-slate-300 rounded-lg p-2.5 text-sm uppercase"
              value={form.jira_project_key}
              onChange={(e) => setForm({ ...form, jira_project_key: e.target.value.toUpperCase() })}
            />
            <p className="text-xs text-gray-400 mt-1">The project key for task sync (found in your Jira project URL)</p>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`p-3 rounded-lg text-sm flex items-center gap-2 ${
              testResult.success
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {testResult.success ? <CheckCircle size={16} /> : <XCircle size={16} />}
              {testResult.message}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={saving}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-4 py-2.5 font-medium disabled:opacity-50 text-sm"
            >
              {saving ? 'Saving...' : 'Save & Connect'}
            </button>
            <button
              type="button"
              onClick={handleTest}
              disabled={testing || !form.jira_base_url}
              className="px-4 py-2.5 border border-slate-300 rounded-lg text-gray-700 hover:bg-slate-50 disabled:opacity-50 text-sm font-medium"
            >
              {testing ? 'Testing...' : 'Test Connection'}
            </button>
          </div>
        </form>
      </div>

      {/* Info Card */}
      <div className="bg-blue-50 rounded-xl border border-blue-200 p-5">
        <h3 className="font-bold text-blue-800 mb-2">How Jira Sync Works</h3>
        <ul className="text-sm text-blue-700 space-y-1.5">
          <li>• Tasks created in TITANS with "Also create in Jira" will appear in your Jira board</li>
          <li>• Tasks created in Jira will auto-sync to the TITANS dashboard</li>
          <li>• Editing title, description, priority, or status syncs both ways</li>
          <li>• Assigning employees in TITANS updates the Jira assignee</li>
          <li>• Assigning in Jira updates the TITANS employee assignment</li>
          <li>• Team members from Jira are auto-imported to the Employees page</li>
        </ul>
      </div>
    </div>
  );
};

export default Settings;
