import axios from 'axios';

const client = axios.create({
  baseURL: '/api',
});

client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Tasks API
export const fetchTasks = (params) => client.get('/tasks', { params });
export const fetchTask = (id) => client.get(`/tasks/${id}`);
export const analyzeTask = (id) => client.post(`/tasks/${id}/analyze`);
export const createTask = (data) => client.post('/tasks', data);
export const updateTask = (id, data) => client.put(`/tasks/${id}`, data);

// Jira Sync API
export const syncFromJira = () => client.post('/tasks/jira/sync');
export const importJiraIssue = (key) => client.post(`/tasks/jira/import/${key}`);
export const getJiraStatus = () => client.get('/tasks/jira/status');

// Employees API
export const fetchEmployees = (params) => client.get('/employees', { params });
export const createEmployee = (data) => client.post('/employees', data);
export const updateEmployee = (id, data) => client.put(`/employees/${id}`, data);
export const fetchEmployeeWorkload = (id) => client.get(`/employees/${id}/workload`);
export const fetchEmployeeHistory = (id) => client.get(`/employees/${id}/history`);
export const syncEmployeesFromJira = () => client.post('/employees/jira/sync');

// Recommendations API
export const generateRecommendations = (taskId) => client.post(`/recommendations/generate/${taskId}`);
export const fetchRecommendations = (taskId) => client.get(`/recommendations/${taskId}`);
export const approveRecommendation = (id) => client.post(`/recommendations/${id}/approve`);
export const overrideRecommendation = (id, data) => client.post(`/recommendations/${id}/override`, data);

// Settings API
export const getJiraSettings = () => client.get('/settings/jira');
export const saveJiraSettings = (data) => client.post('/settings/jira', data);
export const testJiraConnection = () => client.post('/settings/jira/test');
