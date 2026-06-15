import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Team, TeamMember, TeamMetrics } from "@/types";

export const teamKeys = {
  me: ["team", "me"] as const,
  members: ["team", "members"] as const,
  metrics: ["team", "metrics"] as const,
};

export function useMyTeam() {
  return useQuery({
    queryKey: teamKeys.me,
    queryFn: () => api.get<Team>("/teams/me").then((r) => r.data),
  });
}

export function useTeamMembers() {
  return useQuery({
    queryKey: teamKeys.members,
    queryFn: () => api.get<TeamMember[]>("/teams/me/members").then((r) => r.data),
  });
}

export function useTeamMetrics() {
  return useQuery({
    queryKey: teamKeys.metrics,
    queryFn: () => api.get<TeamMetrics>("/teams/me/metrics").then((r) => r.data),
  });
}

export function useCreateTeam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => api.post<Team>("/teams", { name }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: teamKeys.me }),
  });
}

export function useJoinTeam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (invite_code: string) =>
      api.post<Team>("/teams/join", { invite_code }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: teamKeys.me }),
  });
}
