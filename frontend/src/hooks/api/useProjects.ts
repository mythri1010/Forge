import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Project, Paginated, ProjectMetrics } from "@/types";

export const projectKeys = {
  all: ["projects"] as const,
  detail: (id: number) => ["projects", id] as const,
  metrics: (id: number) => ["projects", id, "metrics"] as const,
};

export function useProjects(page = 1) {
  return useQuery({
    queryKey: [...projectKeys.all, page],
    queryFn: () =>
      api.get<Paginated<Project>>("/projects", { params: { page, per_page: 50 } })
        .then((r) => r.data),
  });
}

export function useProject(id: number) {
  return useQuery({
    queryKey: projectKeys.detail(id),
    queryFn: () => api.get<Project>(`/projects/${id}`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useProjectMetrics(id: number) {
  return useQuery({
    queryKey: projectKeys.metrics(id),
    queryFn: () => api.get<ProjectMetrics>(`/projects/${id}/metrics`).then((r) => r.data),
    enabled: !!id,
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      name: string;
      description?: string;
      start_date?: string;
      end_date?: string;
    }) => api.post<Project>("/projects", data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: projectKeys.all }),
  });
}

export function useUpdateProject(id: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Project>) =>
      api.patch<Project>(`/projects/${id}`, data).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: projectKeys.detail(id) });
      qc.invalidateQueries({ queryKey: projectKeys.all });
    },
  });
}
