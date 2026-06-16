"use client";

import { useState, useMemo } from "react";
import toast from "react-hot-toast";
import { useProjectTasks, useChangeTaskStatus, useCreateTask } from "@/hooks/api/useTasks";
import { useTeamMembers } from "@/hooks/api/useTeam";
import { Task, TaskStatus } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { Spinner } from "@/components/ui/Spinner";
import { Modal } from "@/components/ui/Modal";
import { TaskDrawer } from "@/components/project/TaskDrawer";
import { getErrorMessage } from "@/lib/api";
import { Plus, User, Calendar, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import clsx from "clsx";

const COLUMNS: { status: TaskStatus; label: string; color: string }[] = [
  { status: "TODO",        label: "Backlog",      color: "bg-gray-100 text-gray-600" },
  { status: "IN_PROGRESS", label: "In Progress",  color: "bg-blue-100 text-blue-700" },
  { status: "IN_REVIEW",   label: "In Review",    color: "bg-purple-100 text-purple-700" },
  { status: "BLOCKED",     label: "Blocked",      color: "bg-red-100 text-red-700" },
  { status: "DONE",        label: "Done",         color: "bg-green-100 text-green-700" },
];

interface Props { projectId: number }

export function KanbanBoard({ projectId }: Props) {
  const { data, isLoading } = useProjectTasks(projectId);
  const { data: members } = useTeamMembers();
  const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
  const [addingToStatus, setAddingToStatus] = useState<TaskStatus | null>(null);

  const tasksByStatus = useMemo(() => {
    const map: Record<TaskStatus, Task[]> = {
      TODO: [], IN_PROGRESS: [], IN_REVIEW: [], BLOCKED: [], DONE: [],
    };
    for (const task of data?.items ?? []) {
      map[task.status]?.push(task);
    }
    return map;
  }, [data]);

  const memberMap = useMemo(
    () => Object.fromEntries((members ?? []).map((m) => [m.user_id, m.user_name])),
    [members]
  );

  if (isLoading) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  }

  return (
    <div className="flex gap-4 p-6 overflow-x-auto h-full items-start">
      {COLUMNS.map(({ status, label, color }) => (
        <KanbanColumn
          key={status}
          status={status}
          label={label}
          color={color}
          tasks={tasksByStatus[status]}
          memberMap={memberMap}
          projectId={projectId}
          onSelectTask={setSelectedTaskId}
          onAdd={() => setAddingToStatus(status)}
        />
      ))}

      {selectedTaskId && (
        <TaskDrawer
          taskId={selectedTaskId}
          projectId={projectId}
          onClose={() => setSelectedTaskId(null)}
        />
      )}

      {addingToStatus && (
        <QuickAddModal
          projectId={projectId}
          defaultStatus={addingToStatus}
          onClose={() => setAddingToStatus(null)}
        />
      )}
    </div>
  );
}

function KanbanColumn({
  status, label, color, tasks, memberMap, projectId, onSelectTask, onAdd,
}: {
  status: TaskStatus;
  label: string;
  color: string;
  tasks: Task[];
  memberMap: Record<number, string>;
  projectId: number;
  onSelectTask: (id: number) => void;
  onAdd: () => void;
}) {
  return (
    <div className="flex flex-col w-72 shrink-0 bg-gray-50 rounded-xl border border-gray-200">
      {/* Column header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <span className={clsx("badge", color)}>{label}</span>
          <span className="text-xs text-gray-400">{tasks.length}</span>
        </div>
        <button
          onClick={onAdd}
          className="p-1 rounded hover:bg-gray-200 text-gray-400 hover:text-gray-600 transition-colors"
          title={`Add to ${label}`}
        >
          <Plus size={14} />
        </button>
      </div>

      {/* Cards */}
      <div className="flex flex-col gap-2 p-3 min-h-[120px]">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            assigneeName={task.assignee_id ? memberMap[task.assignee_id] : undefined}
            projectId={projectId}
            onClick={() => onSelectTask(task.id)}
          />
        ))}
        {tasks.length === 0 && (
          <p className="text-xs text-gray-300 text-center py-4">No tasks</p>
        )}
      </div>
    </div>
  );
}

function TaskCard({
  task, assigneeName, projectId, onClick,
}: {
  task: Task;
  assigneeName?: string;
  projectId: number;
  onClick: () => void;
}) {
  const changeStatus = useChangeTaskStatus(task.id, projectId);
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== "DONE";

  async function handleStatusChange(e: React.ChangeEvent<HTMLSelectElement>) {
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
      className="bg-white rounded-lg border border-gray-200 p-3 shadow-sm cursor-pointer
                 hover:border-brand-300 hover:shadow-md transition-all group"
    >
      {/* Title + overdue */}
      <div className="flex items-start gap-1.5 mb-2">
        <p className="text-sm font-medium text-gray-900 leading-snug flex-1 group-hover:text-brand-700 transition-colors">
          {task.title}
        </p>
        {isOverdue && <AlertTriangle size={13} className="text-red-400 shrink-0 mt-0.5" />}
      </div>

      {/* Priority + status selector */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <PriorityBadge priority={task.priority} />
        <select
          value={task.status}
          onChange={handleStatusChange}
          onClick={(e) => e.stopPropagation()}
          disabled={changeStatus.isPending}
          className="text-[11px] border border-gray-200 rounded px-1.5 py-0.5 bg-white text-gray-600
                     focus:outline-none focus:border-brand-400 disabled:opacity-50"
        >
          {(["TODO","IN_PROGRESS","IN_REVIEW","DONE","BLOCKED"] as TaskStatus[]).map((s) => (
            <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
          ))}
        </select>
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-3 text-[11px] text-gray-400">
        {assigneeName && (
          <span className="flex items-center gap-1">
            <User size={11} />
            {assigneeName.split(" ")[0]}
          </span>
        )}
        {task.due_date && (
          <span className={clsx("flex items-center gap-1", isOverdue && "text-red-400")}>
            <Calendar size={11} />
            {format(new Date(task.due_date), "MMM d")}
          </span>
        )}
      </div>
    </div>
  );
}

function QuickAddModal({
  projectId, defaultStatus, onClose,
}: {
  projectId: number;
  defaultStatus: TaskStatus;
  onClose: () => void;
}) {
  const create = useCreateTask(projectId);
  const { data: members } = useTeamMembers();
  const [form, setForm] = useState({
    title: "",
    priority: "MEDIUM",
    assignee_id: "",
    due_date: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await create.mutateAsync({
        title: form.title,
        priority: form.priority,
        assignee_id: form.assignee_id ? parseInt(form.assignee_id) : undefined,
        due_date: form.due_date || undefined,
      });
      toast.success("Task created");
      onClose();
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <Modal open onClose={onClose} title={`Add task → ${defaultStatus.replace(/_/g, " ")}`} size="sm">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="label">Title *</label>
          <input
            className="input"
            required
            autoFocus
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="What needs to be done?"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Priority</label>
            <select
              className="input"
              value={form.priority}
              onChange={(e) => setForm({ ...form, priority: e.target.value })}
            >
              {["LOW","MEDIUM","HIGH","CRITICAL"].map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Assignee</label>
            <select
              className="input"
              value={form.assignee_id}
              onChange={(e) => setForm({ ...form, assignee_id: e.target.value })}
            >
              <option value="">Unassigned</option>
              {members?.map((m) => (
                <option key={m.user_id} value={m.user_id}>{m.user_name}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className="label">Due date</label>
          <input
            type="date"
            className="input"
            value={form.due_date}
            onChange={(e) => setForm({ ...form, due_date: e.target.value })}
          />
        </div>
        <div className="flex justify-end gap-2 pt-1">
          <button type="button" className="btn-secondary" onClick={onClose}>Cancel</button>
          <button type="submit" className="btn-primary" disabled={create.isPending}>
            {create.isPending ? "Adding…" : "Add task"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
