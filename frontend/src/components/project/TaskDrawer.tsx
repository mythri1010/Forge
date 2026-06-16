"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { useTask, useUpdateTask, useChangeTaskStatus } from "@/hooks/api/useTasks";
import { useTaskWorklogs, useCreateWorklog, useDeleteWorklog } from "@/hooks/api/useWorklogs";
import { useTeamMembers } from "@/hooks/api/useTeam";
import { TaskStatus, TaskPriority } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { PriorityBadge } from "@/components/ui/PriorityBadge";
import { Spinner } from "@/components/ui/Spinner";
import { getErrorMessage } from "@/lib/api";
import { X, Clock, Plus, Trash2, Edit2, Check } from "lucide-react";
import { format } from "date-fns";

interface Props {
  taskId: number;
  projectId: number;
  onClose: () => void;
}

export function TaskDrawer({ taskId, projectId, onClose }: Props) {
  const { data: task, isLoading } = useTask(taskId);
  const { data: worklogs } = useTaskWorklogs(taskId);
  const { data: members } = useTeamMembers();
  const changeStatus = useChangeTaskStatus(taskId, projectId);
  const updateTask = useUpdateTask(taskId, projectId);
  const createWorklog = useCreateWorklog(taskId);
  const deleteWorklog = useDeleteWorklog(taskId);

  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");
  const [worklogForm, setWorklogForm] = useState({ hours: "", date: "", note: "" });
  const [showWorklogForm, setShowWorklogForm] = useState(false);

  async function handleStatusChange(to_status: TaskStatus) {
    try {
      await changeStatus.mutateAsync(to_status);
      toast.success("Status updated");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  async function handleSaveTitle() {
    if (!titleDraft.trim()) return;
    try {
      await updateTask.mutateAsync({ title: titleDraft.trim() });
      toast.success("Title updated");
      setEditingTitle(false);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  async function handleAssigneeChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const val = e.target.value;
    try {
      await updateTask.mutateAsync({ assignee_id: val ? parseInt(val) : null });
      toast.success("Assignee updated");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  async function handleLogTime(e: React.FormEvent) {
    e.preventDefault();
    const hours = parseFloat(worklogForm.hours);
    if (!hours || hours <= 0) return;
    try {
      await createWorklog.mutateAsync({
        hours,
        date: worklogForm.date || undefined,
        note: worklogForm.note || undefined,
      });
      toast.success("Time logged");
      setWorklogForm({ hours: "", date: "", note: "" });
      setShowWorklogForm(false);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  async function handleDeleteWorklog(wid: number) {
    try {
      await deleteWorklog.mutateAsync(wid);
      toast.success("Removed");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  const totalHours = (worklogs?.items ?? []).reduce((s, w) => s + w.hours, 0);

  return (
    /* Overlay */
    <div className="fixed inset-0 z-40 flex justify-end">
      <div className="absolute inset-0 bg-black/20" onClick={onClose} />
      <aside className="relative w-full max-w-lg bg-white shadow-xl flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 shrink-0">
          <h2 className="text-sm font-semibold text-gray-700">Task detail</h2>
          <button onClick={onClose} className="p-1.5 rounded hover:bg-gray-100 text-gray-400">
            <X size={16} />
          </button>
        </div>

        {isLoading || !task ? (
          <div className="flex justify-center py-16"><Spinner /></div>
        ) : (
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
            {/* Title */}
            <div>
              {editingTitle ? (
                <div className="flex gap-2">
                  <input
                    className="input flex-1"
                    autoFocus
                    value={titleDraft}
                    onChange={(e) => setTitleDraft(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") handleSaveTitle(); }}
                  />
                  <button className="btn-primary p-2" onClick={handleSaveTitle}>
                    <Check size={14} />
                  </button>
                  <button className="btn-secondary p-2" onClick={() => setEditingTitle(false)}>
                    <X size={14} />
                  </button>
                </div>
              ) : (
                <div className="flex items-start gap-2 group">
                  <h3 className="text-base font-semibold text-gray-900 flex-1">{task.title}</h3>
                  <button
                    className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:bg-gray-100 text-gray-400 transition-all shrink-0"
                    onClick={() => { setTitleDraft(task.title); setEditingTitle(true); }}
                  >
                    <Edit2 size={13} />
                  </button>
                </div>
              )}
            </div>

            {/* Status + Priority */}
            <div className="flex flex-wrap gap-3">
              <div>
                <p className="text-xs text-gray-400 mb-1">Status</p>
                <select
                  className="text-sm border border-gray-200 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:border-brand-400"
                  value={task.status}
                  onChange={(e) => handleStatusChange(e.target.value as TaskStatus)}
                  disabled={changeStatus.isPending}
                >
                  {(["TODO","IN_PROGRESS","IN_REVIEW","DONE","BLOCKED"] as TaskStatus[]).map((s) => (
                    <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
                  ))}
                </select>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Priority</p>
                <select
                  className="text-sm border border-gray-200 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:border-brand-400"
                  value={task.priority}
                  onChange={async (e) => {
                    try {
                      await updateTask.mutateAsync({ priority: e.target.value as TaskPriority });
                    } catch (err) { toast.error(getErrorMessage(err)); }
                  }}
                >
                  {(["LOW","MEDIUM","HIGH","CRITICAL"] as TaskPriority[]).map((p) => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div>
                <p className="text-xs text-gray-400 mb-1">Assignee</p>
                <select
                  className="text-sm border border-gray-200 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:border-brand-400"
                  value={task.assignee_id ?? ""}
                  onChange={handleAssigneeChange}
                >
                  <option value="">Unassigned</option>
                  {members?.map((m) => (
                    <option key={m.user_id} value={m.user_id}>{m.user_name}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Due date */}
            <div>
              <p className="text-xs text-gray-400 mb-1">Due date</p>
              <input
                type="date"
                className="input w-40"
                value={task.due_date ?? ""}
                onChange={async (e) => {
                  try {
                    await updateTask.mutateAsync({ due_date: e.target.value || null });
                  } catch (err) { toast.error(getErrorMessage(err)); }
                }}
              />
            </div>

            {/* Description */}
            {task.description && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Description</p>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{task.description}</p>
              </div>
            )}

            {/* Worklogs */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide flex items-center gap-1.5">
                  <Clock size={12} />
                  Time logged
                  {totalHours > 0 && (
                    <span className="font-normal text-gray-400">({totalHours.toFixed(1)}h total)</span>
                  )}
                </p>
                <button
                  className="btn-secondary text-xs py-1"
                  onClick={() => setShowWorklogForm(!showWorklogForm)}
                >
                  <Plus size={12} /> Log time
                </button>
              </div>

              {showWorklogForm && (
                <form onSubmit={handleLogTime} className="bg-gray-50 rounded-lg p-3 mb-3 space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="label text-xs">Hours *</label>
                      <input
                        type="number"
                        step="0.25"
                        min="0.25"
                        max="24"
                        className="input text-sm"
                        required
                        value={worklogForm.hours}
                        onChange={(e) => setWorklogForm({ ...worklogForm, hours: e.target.value })}
                        placeholder="1.5"
                      />
                    </div>
                    <div>
                      <label className="label text-xs">Date</label>
                      <input
                        type="date"
                        className="input text-sm"
                        value={worklogForm.date}
                        onChange={(e) => setWorklogForm({ ...worklogForm, date: e.target.value })}
                      />
                    </div>
                  </div>
                  <div>
                    <label className="label text-xs">Note</label>
                    <input
                      className="input text-sm"
                      value={worklogForm.note}
                      onChange={(e) => setWorklogForm({ ...worklogForm, note: e.target.value })}
                      placeholder="What did you work on?"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button type="button" className="btn-secondary text-xs py-1"
                      onClick={() => setShowWorklogForm(false)}>Cancel</button>
                    <button type="submit" className="btn-primary text-xs py-1"
                      disabled={createWorklog.isPending}>
                      {createWorklog.isPending ? "Saving…" : "Save"}
                    </button>
                  </div>
                </form>
              )}

              <div className="space-y-1.5">
                {(worklogs?.items ?? []).length === 0 ? (
                  <p className="text-xs text-gray-400">No time logged yet.</p>
                ) : (
                  (worklogs?.items ?? []).map((w) => (
                    <div key={w.id} className="flex items-center gap-2 text-xs text-gray-600 py-1 group">
                      <Clock size={11} className="text-gray-400 shrink-0" />
                      <span className="font-medium">{w.hours}h</span>
                      <span className="text-gray-400">{format(new Date(w.date), "MMM d")}</span>
                      {w.note && <span className="text-gray-400 truncate flex-1">— {w.note}</span>}
                      <button
                        onClick={() => handleDeleteWorklog(w.id)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:text-red-500 text-gray-300 transition-all"
                      >
                        <Trash2 size={11} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Meta */}
            <div className="border-t border-gray-100 pt-3 text-xs text-gray-400 space-y-1">
              <p>Created {format(new Date(task.created_at), "MMM d, yyyy")}</p>
              {task.completed_at && (
                <p>Completed {format(new Date(task.completed_at), "MMM d, yyyy")}</p>
              )}
            </div>
          </div>
        )}
      </aside>
    </div>
  );
}
