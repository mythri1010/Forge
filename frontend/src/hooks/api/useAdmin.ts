import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { AdminTeamRow, Feedback, TimeseriesRow } from "@/types";

export const adminKeys = {
  overview: ["admin", "overview"] as const,
  timeseries: (weeks: number) => ["admin", "timeseries", weeks] as const,
  feedback: ["admin", "feedback"] as const,
};

export function useAdminOverview() {
  return useQuery({
    queryKey: adminKeys.overview,
    queryFn: () => api.get<AdminTeamRow[]>("/admin/overview").then((r) => r.data),
  });
}

export function useAdminTimeseries(weeks = 8) {
  return useQuery({
    queryKey: adminKeys.timeseries(weeks),
    queryFn: () =>
      api
        .get<TimeseriesRow[]>("/admin/usage-timeseries", { params: { weeks } })
        .then((r) => r.data),
  });
}

export function useAdminFeedback() {
  return useQuery({
    queryKey: adminKeys.feedback,
    queryFn: () => api.get<Feedback[]>("/admin/feedback").then((r) => r.data),
  });
}

export function useUpdateFeedbackStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.patch(`/admin/feedback/${id}`, { status }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: adminKeys.feedback }),
  });
}
