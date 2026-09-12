import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { generateRecommendations, fetchRecommendations, approveRecommendation, overrideRecommendation } from '../api/client';

export const useGenerateRecommendations = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (taskId) => generateRecommendations(taskId),
    onSuccess: (data, taskId) => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', taskId] });
    },
  });
};

export const useRecommendations = (taskId) => {
  return useQuery({
    queryKey: ['recommendations', taskId],
    queryFn: () => fetchRecommendations(taskId),
    enabled: !!taskId,
  });
};

export const useApproveRecommendation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => approveRecommendation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};

export const useOverrideRecommendation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => overrideRecommendation(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
};
