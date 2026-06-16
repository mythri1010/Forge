import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Worklog, Paginated } from "@/types";

export const worklogKeys = {
  forTask: (taskId: number) => ["worklogs", "task", taskId] as const,
};

export function useTaskWorklogs(taskId: number) {
  return useQuery({
    queryKey: worklogKeys.forTask(taskId),
    queryFn: () =>
      api.get<Paginated<Worklog>>(`/worklogs/task/${taskId}`).then((r) => r.data),
    enabled: !!taskId,
  });
}

export function useCreateWorklog(taskId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { hours: number; date?: string; note?: string }) =>
      api.post<Worklog>(`/worklogs/task/${taskId}`, data).then((r) => r.data),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: worklogKeys.forTask(taskId) }),
  });
}

export function useDeleteWorklog(taskId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (worklogId: number) => api.delete(`/worklogs/${worklogId}`),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: worklogKeys.forTask(taskId) }),
  });
}
