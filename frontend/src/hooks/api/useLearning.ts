import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { LearningLog, Paginated } from "@/types";

export const learningKeys = {
  mine: ["learning"] as const,
};

export function useMyLearningLogs(page = 1) {
  return useQuery({
    queryKey: [...learningKeys.mine, page],
    queryFn: () =>
      api
        .get<Paginated<LearningLog>>("/learning", { params: { page, per_page: 50 } })
        .then((r) => r.data),
  });
}

export function useCreateLearningLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { summary: string; date?: string; task_id?: number }) =>
      api.post<LearningLog>("/learning", data).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: learningKeys.mine }),
  });
}

export function useDeleteLearningLog() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.delete(`/learning/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: learningKeys.mine }),
  });
}
