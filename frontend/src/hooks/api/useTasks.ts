import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Task, TaskStatus, Paginated, StatusHistory } from "@/types";

export const taskKeys = {
  forProject: (pid: number, filters?: object) =>
    ["tasks", "project", pid, filters] as const,
  detail: (id: number) => ["tasks", id] as const,
  history: (id: number) => ["tasks", id, "history"] as const,
};

interface TaskFilters {
  status?: TaskStatus;
  assignee_id?: number;
  priority?: string;
  page?: number;
}

export function useProjectTasks(projectId: number, filters: TaskFilters = {}) {
  return useQuery({
    queryKey: taskKeys.forProject(projectId, filters),
    queryFn: () =>
      api
        .get<Paginated<Task>>(`/tasks/project/${projectId}`, {
          params: { per_page: 200, ...filters },
        })
        .then((r) => r.data),
    enabled: !!projectId,
  });
}

export function useTask(id: number) {
  return useQuery({
    queryKey: taskKeys.detail(id),
    queryFn: () => api.get<Task>(`/tasks/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useTaskHistory(id: number) {
  return useQuery({
    queryKey: taskKeys.history(id),
    queryFn: () =>
      api.get<StatusHistory[]>(`/tasks/${id}/history`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateTask(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      title: string;
      description?: string;
      priority?: string;
      assignee_id?: number;
      due_date?: string;
    }) => api.post<Task>(`/tasks/project/${projectId}`, data).then((r) => r.data),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["tasks", "project", projectId] }),
  });
}

export function useUpdateTask(taskId: number, projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Task>) =>
      api.patch<Task>(`/tasks/${taskId}`, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
      qc.invalidateQueries({ queryKey: ["tasks", "project", projectId] });
    },
  });
}

export function useChangeTaskStatus(taskId: number, projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (to_status: TaskStatus) =>
      api.post<Task>(`/tasks/${taskId}/status`, { to_status }).then((r) => r.data),
    onSuccess: (updated) => {
      qc.setQueryData(taskKeys.detail(taskId), updated);
      qc.invalidateQueries({ queryKey: ["tasks", "project", projectId] });
    },
  });
}

export function useDeleteTask(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (taskId: number) => api.delete(`/tasks/${taskId}`),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["tasks", "project", projectId] }),
  });
}
