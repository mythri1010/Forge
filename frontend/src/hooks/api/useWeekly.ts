import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { WeeklyGoal, WeeklyReflection, Paginated } from "@/types";

export const weeklyKeys = {
  goals: (projectId: number) => ["weekly", "goals", projectId] as const,
  reflections: (goalId: number) => ["weekly", "reflections", goalId] as const,
};

export function useWeeklyGoals(projectId: number) {
  return useQuery({
    queryKey: weeklyKeys.goals(projectId),
    queryFn: () =>
      api
        .get<Paginated<WeeklyGoal>>(`/weekly/goals/project/${projectId}`)
        .then((r) => r.data),
    enabled: !!projectId,
  });
}

export function useReflections(goalId: number) {
  return useQuery({
    queryKey: weeklyKeys.reflections(goalId),
    queryFn: () =>
      api
        .get<WeeklyReflection[]>(`/weekly/goals/${goalId}/reflections`)
        .then((r) => r.data),
    enabled: !!goalId,
  });
}

export function useCreateGoal(projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { goal_text: string; week_start_date: string }) =>
      api.post<WeeklyGoal>(`/weekly/goals/project/${projectId}`, data).then((r) => r.data),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: weeklyKeys.goals(projectId) }),
  });
}

export function useSubmitReflection(goalId: number, projectId: number) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      met_goal: boolean;
      blockers?: string;
      process_notes?: string;
      perceived_helpfulness?: number;
    }) =>
      api
        .post<WeeklyReflection>(`/weekly/goals/${goalId}/reflections`, data)
        .then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: weeklyKeys.reflections(goalId) });
      qc.invalidateQueries({ queryKey: weeklyKeys.goals(projectId) });
    },
  });
}
