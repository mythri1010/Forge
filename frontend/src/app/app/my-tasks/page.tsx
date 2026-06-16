"use client";

import { useMemo, useState } from "react";
import toast from "react-hot-toast";
import { Header } from "@/components/layout/Header";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { MetricCard } from "@/components/ui/MetricCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { TaskDrawer } from "@/components/project/TaskDrawer";
import { useProjects } from "@/hooks/api/useProjects";
import { useProjectTasks, useChangeTaskStatus } from "@/hooks/api/useTasks";
import { useTeamMetrics } from "@/hooks/api/useTeam";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/api";
import { Task, TaskStatus } from "@/types";
import { CheckSquare, Clock, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";
import clsx from "clsx";

function useAllMyTasks(userId: number | undefined) {
  const { data: projects } = useProjects();
  const firstProject = projects?.items?.[0];
  const { data: tasks, isLoading } = useProjectTasks(firstProject?.id ?? 0, {
    assignee_id: userId,
  });
  return { tasks: tasks?.items ?? [], isLoading };
}

export default function MyTasksPage() {
  const { user } = useAuth();
  const { data: metrics, isLoading: metricsLoading } = useTeamMetrics();
  const { tasks, isLoading } = useAllMyTasks(user?.user_id);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);

  const myStats = useMemo(
    () => metrics?.member_stats?.find((m) => m.user_id === user?.user_id),
    [metrics, user]
  );

  const activeTasks = tasks.filter((t) => !["DONE"].includes(t.status));
  const doneTasks = tasks.filter((t) => t.status === "DONE").slice(0, 10);

  // Build a simple per-day hours chart from member stats placeholder
  const hoursChartData = useMemo(() => {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const totalHours = myStats?.total_hours_last_7d ?? 0;
    const avg = totalHours / 7;
    return days.map((day) => ({
      day,
      hours: parseFloat((avg * (0.5 + Math.random())).toFixed(1)),
    }));
  }, [myStats]);

  return (
    <div className="flex flex-col h-full">
      <Header title="My Tasks" />
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">
        {/* Stats row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard label="Active tasks" value={activeTasks.length} accent="blue" loading={isLoading} />
          <MetricCard label="Done this week" value={myStats?.tasks_done_last_7d} accent="green" loading={metricsLoading} />
          <MetricCard
            label="Hours this week"
            value={myStats ? `${myStats.total_hours_last_7d.toFixed(1)}h` : null}
            loading={metricsLoading}
          />
          <MetricCard
            label="Avg cycle time"
            value={myStats?.avg_cycle_time_days != null ? `${myStats.avg_cycle_time_days.toFixed(1)}d` : null}
            loading={metricsLoading}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Active tasks list */}
          <div className="lg:col-span-2 space-y-4">
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                In progress & blocked
              </h2>
              <div className="card divide-y divide-gray-100">
                {isLoading ? (
                  <div className="flex justify-center py-8"><Spinner /></div>
                ) : activeTasks.length === 0 ? (
                  <EmptyState icon={CheckSquare} title="No active tasks" description="You're all caught up." />
                ) : (
                  activeTasks.map((task) => (
                    <MyTaskRow
                      key={task.id}
                      task={task}
                      onClick={() => setSelectedTask(task)}
                    />
                  ))
                )}
              </div>
            </section>

            {doneTasks.length > 0 && (
              <section>
                <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
                  Recently completed
                </h2>
                <div className="card divide-y divide-gray-100">
                  {doneTasks.map((task) => (
                    <MyTaskRow
                      key={task.id}
                      task={task}
                      onClick={() => setSelectedTask(task)}
                    />
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Hours chart */}
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-2">
              Hours logged — this week
            </h2>
            <div className="card p-4">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={hoursChartData} margin={{ left: -20, right: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => [`${v}h`, "Hours"]} />
                  <Bar dataKey="hours" fill="#6366f1" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {selectedTask && (
        <TaskDrawer
          taskId={selectedTask.id}
          projectId={selectedTask.project_id}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </div>
  );
}

function MyTaskRow({ task, onClick }: { task: Task; onClick: () => void }) {
  const changeStatus = useChangeTaskStatus(task.id, task.project_id);
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== "DONE";

  async function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    e.stopPropagation();
    try {
      await changeStatus.mutateAsync(e.target.value as TaskStatus);
      toast.success("Status updated");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <div
      onClick={onClick}
      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5">
          <p className="text-sm font-medium text-gray-900 truncate">{task.title}</p>
          {isOverdue && <AlertTriangle size={13} className="text-red-400 shrink-0" />}
        </div>
        {task.due_date && (
          <p className={clsx("text-xs mt-0.5 flex items-center gap-1",
            isOverdue ? "text-red-400" : "text-gray-400")}>
            <Clock size={11} />
            {format(new Date(task.due_date), "MMM d")}
          </p>
        )}
      </div>
      <PriorityBadge priority={task.priority} />
      <StatusBadge status={task.status} />
      <select
        className="text-xs border border-gray-200 rounded px-2 py-1 bg-white text-gray-600"
        value={task.status}
        onChange={handleChange}
        disabled={changeStatus.isPending}
        onClick={(e) => e.stopPropagation()}
      >
        {(["TODO","IN_PROGRESS","IN_REVIEW","DONE","BLOCKED"] as TaskStatus[]).map((s) => (
          <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
        ))}
      </select>
    </div>
  );
}
