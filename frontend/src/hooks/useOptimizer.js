import { useMutation, useQueryClient } from '@tanstack/react-query';
import { runOptimizer, previewOptimization, applyOptimization } from '../api/client';

export const useRunOptimizer = () => {
  return useMutation({
    mutationFn: () => runOptimizer(),
  });
};

export const usePreviewOptimization = () => {
  return useMutation({
    mutationFn: () => previewOptimization(),
  });
};

export const useApplyOptimization = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => applyOptimization(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
  });
};
