"use client";

import { useMemo } from "react";
import toast from "react-hot-toast";
import { Header } from "@/components/layout/Header";
import { MetricCard } from "@/components/ui/MetricCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { ThroughputChart } from "@/components/charts/ThroughputChart";
import { useTeamMetrics } from "@/hooks/api/useTeam";
import { useProjects } from "@/hooks/api/useProjects";
import { useProjectTasks, useChangeTaskStatus } from "@/hooks/api/useTasks";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";
import { Task, TaskStatus } from "@/types";
import { CheckSquare, Clock, AlertTriangle } from "lucide-react";
import { format } from "date-fns";

// Shows all active tasks across all projects for the current user
function useMyActiveTasks(userId: number | undefined) {
  const { data: projects } = useProjects();
  // We pick the first project for simplicity — real app would combine all
  const firstProject = projects?.items?.[0];
  const { data: tasks, isLoading } = useProjectTasks(firstProject?.id ?? 0, {
    assignee_id: userId,
  });
  const active = useMemo(
    () =>
      tasks?.items?.filter((t) =>
        ["IN_PROGRESS", "BLOCKED", "IN_REVIEW"].includes(t.status)
      ) ?? [],
    [tasks]
  );
  return { tasks: active, isLoading };
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: metrics, isLoading: metricsLoading } = useTeamMetrics();

  const myStats = useMemo(
    () => metrics?.member_stats?.find((m) => m.user_id === user?.user_id),
    [metrics, user]
  );

  const { tasks: activeTasks, isLoading: tasksLoading } = useMyActiveTasks(user?.user_id);

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Dashboard"
        actions={
          <span className="text-xs text-gray-400">
            {format(new Date(), "EEEE, MMMM d")}
          </span>
        }
      />

      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Metric cards */}
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
            Your stats this week
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="My WIP"
              value={myStats?.current_wip}
              sub="open tasks"
              accent={myStats?.current_wip && myStats.current_wip > 3 ? "yellow" : "default"}
              loading={metricsLoading}
            />
            <MetricCard
              label="Hours logged"
              value={myStats ? `${myStats.total_hours_last_7d.toFixed(1)}h` : null}
              sub="last 7 days"
              accent="blue"
              loading={metricsLoading}
            />
            <MetricCard
              label="Tasks done"
              value={myStats?.tasks_done_last_7d}
              sub="last 7 days"
              accent="green"
              loading={metricsLoading}
            />
            <MetricCard
              label="Avg cycle time"
              value={
                myStats?.avg_cycle_time_days != null
                  ? `${myStats.avg_cycle_time_days.toFixed(1)}d`
                  : null
              }
              sub="time in-progress → done"
              loading={metricsLoading}
            />
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Active tasks */}
          <section className="lg:col-span-2">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
              My active tasks
            </h2>
            <div className="card divide-y divide-gray-100">
              {tasksLoading ? (
                <div className="flex justify-center py-10">
                  <Spinner />
                </div>
              ) : activeTasks.length === 0 ? (
                <EmptyState
                  icon={CheckSquare}
                  title="All clear!"
                  description="No active tasks right now."
                />
              ) : (
                activeTasks.map((task) => (
                  <ActiveTaskRow key={task.id} task={task} />
                ))
              )}
            </div>
          </section>

          {/* Throughput chart */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">
              Team throughput
            </h2>
            <div className="card p-4">
              <ThroughputChart metrics={metrics} loading={metricsLoading} />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function ActiveTaskRow({ task }: { task: Task }) {
  const changeStatus = useChangeTaskStatus(task.id, task.project_id);

  async function handleStatusChange(to_status: TaskStatus) {
    try {
      await changeStatus.mutateAsync(to_status);
      toast.success(`Moved to ${to_status.replace(/_/g, " ")}`);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  const isOverdue =
    task.due_date && new Date(task.due_date) < new Date() && task.status !== "DONE";

  return (
    <div className="flex items-center gap-3 px-4 py-3">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-gray-900 truncate">{task.title}</p>
          {isOverdue && <AlertTriangle size={13} className="text-red-500 shrink-0" />}
        </div>
        {task.due_date && (
          <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
            <Clock size={11} />
            Due {format(new Date(task.due_date), "MMM d")}
          </p>
        )}
      </div>
      <StatusBadge status={task.status} />
      <select
        className="text-xs border border-gray-200 rounded px-2 py-1 text-gray-600 bg-white"
        value={task.status}
        onChange={(e) => handleStatusChange(e.target.value as TaskStatus)}
        disabled={changeStatus.isPending}
      >
        {(["TODO", "IN_PROGRESS", "IN_REVIEW", "DONE", "BLOCKED"] as TaskStatus[]).map((s) => (
          <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
        ))}
      </select>
    </div>
  );
}
