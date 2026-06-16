"use client";

import { useState } from "react";
import { useProjectTasks, useChangeTaskStatus } from "@/hooks/api/useTasks";
import { useTeamMembers } from "@/hooks/api/useTeam";
import { TaskStatus, TaskPriority } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { TaskDrawer } from "@/components/project/TaskDrawer";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/lib/api";
import { CheckSquare, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import clsx from "clsx";

const ALL_STATUSES: TaskStatus[] = ["TODO","IN_PROGRESS","IN_REVIEW","BLOCKED","DONE"];

interface Props { projectId: number }

export function TaskListTab({ projectId }: Props) {
  const [filterStatus, setFilterStatus] = useState<TaskStatus | "">("");
  const [filterAssignee, setFilterAssignee] = useState<string>("");
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);

  const { data: members } = useTeamMembers();
  const { data, isLoading } = useProjectTasks(projectId, {
    status: filterStatus || undefined,
    assignee_id: filterAssignee ? parseInt(filterAssignee) : undefined,
  });

  if (isLoading) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  }

  const tasks = data?.items ?? [];

  return (
    <div className="p-6">
      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          className="input w-40"
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value as TaskStatus | "")}
        >
          <option value="">All statuses</option>
          {ALL_STATUSES.map((s) => (
            <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
          ))}
        </select>
        <select
          className="input w-44"
          value={filterAssignee}
          onChange={(e) => setFilterAssignee(e.target.value)}
        >
          <option value="">All members</option>
          {members?.map((m) => (
            <option key={m.user_id} value={m.user_id}>{m.user_name}</option>
          ))}
        </select>
        <span className="text-xs text-gray-400 self-center ml-auto">
          {tasks.length} task{tasks.length !== 1 ? "s" : ""}
        </span>
      </div>

      {tasks.length === 0 ? (
        <EmptyState icon={CheckSquare} title="No tasks match the filters" />
      ) : (
        <div className="card divide-y divide-gray-100 overflow-hidden">
          {/* Table header */}
          <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-4 px-4 py-2 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wide">
            <span>Task</span>
            <span>Priority</span>
            <span>Status</span>
            <span>Assignee</span>
            <span>Due</span>
          </div>
          {tasks.map((task) => {
            const isOverdue =
              task.due_date &&
              new Date(task.due_date) < new Date() &&
              task.status !== "DONE";
            const assignee = members?.find((m) => m.user_id === task.assignee_id);

            return (
              <div
                key={task.id}
                onClick={() => setSelectedTaskId(task.id)}
                className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-4 items-center px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-2 min-w-0">
                  {isOverdue && <AlertTriangle size={13} className="text-red-400 shrink-0" />}
                  <span className="text-sm font-medium text-gray-900 truncate">{task.title}</span>
                </div>
                <PriorityBadge priority={task.priority} />
                <StatusBadge status={task.status} />
                <span className="text-xs text-gray-500">
                  {assignee ? assignee.user_name.split(" ")[0] : "—"}
                </span>
                <span className={clsx("text-xs", isOverdue ? "text-red-500 font-medium" : "text-gray-400")}>
                  {task.due_date ? format(new Date(task.due_date), "MMM d") : "—"}
                </span>
              </div>
            );
          })}
        </div>
      )}

      {selectedTaskId && (
        <TaskDrawer
          taskId={selectedTaskId}
          projectId={projectId}
          onClose={() => setSelectedTaskId(null)}
        />
      )}
    </div>
  );
}
