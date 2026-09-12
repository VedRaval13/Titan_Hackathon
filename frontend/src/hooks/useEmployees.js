import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchEmployees, createEmployee, updateEmployee, fetchEmployeeWorkload, fetchEmployeeHistory, syncEmployeesFromJira } from '../api/client';

export const useEmployees = (filters) => {
  return useQuery({
    queryKey: ['employees', filters],
    queryFn: () => fetchEmployees(filters),
  });
};

export const useCreateEmployee = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => createEmployee(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
  });
};

export const useUpdateEmployee = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) => updateEmployee(id, data),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      queryClient.invalidateQueries({ queryKey: ['employee', variables.id] });
    },
  });
};

export const useEmployeeWorkload = (id) => {
  return useQuery({
    queryKey: ['employeeWorkload', id],
    queryFn: () => fetchEmployeeWorkload(id),
    enabled: !!id,
  });
};

export const useEmployeeHistory = (id) => {
  return useQuery({
    queryKey: ['employeeHistory', id],
    queryFn: () => fetchEmployeeHistory(id),
    enabled: !!id,
  });
};

export const useSyncEmployeesFromJira = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => syncEmployeesFromJira(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
    },
  });
};
