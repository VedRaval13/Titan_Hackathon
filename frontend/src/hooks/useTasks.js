import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchTasks, fetchTask, analyzeTask, createTask, updateTask, syncFromJira, importJiraIssue, getJiraStatus } from '../api/client';

export const useTasks = (filters) => {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => fetchTasks(filters),
  });
};

export const useTask = (id) => {
  return useQuery({
    queryKey: ['task', id],
    queryFn: () => fetchTask(id),
    enabled: !!id,
  });
};

export const useAnalyzeTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => analyzeTask(id),
    onSuccess: (data, id) => {
      queryClient.invalidateQueries({ queryKey: ['task', id] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
};

export const useCreateTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => createTask(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
};

export const useUpdateTask = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => updateTask(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
};

export const useSyncFromJira = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => syncFromJira(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
};

export const useImportJiraIssue = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (key) => importJiraIssue(key),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
};

export const useJiraStatus = () => {
  return useQuery({
    queryKey: ['jira-status'],
    queryFn: () => getJiraStatus(),
    staleTime: 60000,
  });
};
