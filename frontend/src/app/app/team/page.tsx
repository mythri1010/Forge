"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { Header } from "@/components/layout/Header";
import { useMyTeam, useTeamMembers, useCreateTeam, useJoinTeam } from "@/hooks/api/useTeam";
import { getErrorMessage } from "@/lib/api";
import { Copy, Users } from "lucide-react";
import { format } from "date-fns";

export default function TeamPage() {
  const { data: team, isLoading } = useMyTeam();
  const { data: members } = useTeamMembers();
  const createTeam = useCreateTeam();
  const joinTeam = useJoinTeam();

  const [teamName, setTeamName] = useState("");
  const [inviteCode, setInviteCode] = useState("");
  const [mode, setMode] = useState<"create" | "join">("create");

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createTeam.mutateAsync(teamName);
      toast.success("Team created!");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  async function handleJoin(e: React.FormEvent) {
    e.preventDefault();
    try {
      await joinTeam.mutateAsync(inviteCode);
      toast.success("Joined team!");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  if (team) {
    return (
      <div className="flex flex-col h-full">
        <Header title="My Team" />
        <div className="flex-1 p-6 space-y-5 max-w-lg">
          <div className="card p-5 space-y-3">
            <h3 className="font-semibold text-gray-900">{team.name}</h3>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Invite code:</span>
              <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">{team.invite_code}</code>
              <button
                onClick={() => { navigator.clipboard.writeText(team.invite_code); toast.success("Copied!"); }}
                className="p-1 rounded hover:bg-gray-100 text-gray-400"
              >
                <Copy size={13} />
              </button>
            </div>
            <p className="text-xs text-gray-400">
              Created {format(new Date(team.created_at), "MMM d, yyyy")}
            </p>
          </div>

          <div className="card p-5">
            <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <Users size={15} />
              Members ({members?.length ?? 0})
            </h4>
            <div className="space-y-2">
              {members?.map((m) => (
                <div key={m.id} className="flex items-center gap-3 text-sm">
                  <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
                    <span className="text-brand-700 text-xs font-medium">
                      {m.user_name.charAt(0)}
                    </span>
                  </div>
                  <span className="text-gray-800 flex-1">{m.user_name}</span>
                  <span className="text-xs text-gray-400">{m.role_in_team.replace(/_/g, " ")}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header title="Join a Team" />
      <div className="flex-1 p-6 max-w-md space-y-4">
        <p className="text-sm text-gray-500">You're not in a team yet. Create one or join with an invite code.</p>

        <div className="flex gap-2">
          <button
            className={mode === "create" ? "btn-primary" : "btn-secondary"}
            onClick={() => setMode("create")}
          >Create team</button>
          <button
            className={mode === "join" ? "btn-primary" : "btn-secondary"}
            onClick={() => setMode("join")}
          >Join team</button>
        </div>

        {mode === "create" ? (
          <form onSubmit={handleCreate} className="card p-5 space-y-4">
            <div>
              <label className="label">Team name *</label>
              <input
                className="input"
                required
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
                placeholder="e.g. Team Phoenix"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={createTeam.isPending}>
              {createTeam.isPending ? "Creating…" : "Create team"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleJoin} className="card p-5 space-y-4">
            <div>
              <label className="label">Invite code *</label>
              <input
                className="input font-mono"
                required
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                placeholder="Paste invite code here"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={joinTeam.isPending}>
              {joinTeam.isPending ? "Joining…" : "Join team"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
