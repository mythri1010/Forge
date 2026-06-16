"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { Header } from "@/components/layout/Header";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useMyLearningLogs, useCreateLearningLog, useDeleteLearningLog } from "@/hooks/api/useLearning";
import { LearningLog } from "@/types";
import { getErrorMessage } from "@/lib/api";
import { BookOpen, Trash2, Download } from "lucide-react";
import { format } from "date-fns";

export default function LearningLogPage() {
  const { data, isLoading } = useMyLearningLogs();
  const createLog = useCreateLearningLog();
  const deleteLog = useDeleteLearningLog();
  const [form, setForm] = useState({ summary: "", date: "" });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.summary.trim()) return;
    try {
      await createLog.mutateAsync({
        summary: form.summary,
        date: form.date || undefined,
      });
      toast.success("Entry added");
      setForm({ summary: "", date: "" });
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteLog.mutateAsync(id);
      toast.success("Entry deleted");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  function handleExport() {
    const entries = data?.items ?? [];
    const json = JSON.stringify(entries, null, 2);
    navigator.clipboard.writeText(json);
    toast.success("Copied to clipboard as JSON");
  }

  const entries = data?.items ?? [];

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Learning Log"
        actions={
          entries.length > 0 ? (
            <button className="btn-secondary" onClick={handleExport}>
              <Download size={14} />
              Export
            </button>
          ) : undefined
        }
      />

      <div className="flex-1 p-6 space-y-5 overflow-y-auto max-w-2xl w-full mx-auto">
        {/* Add entry form */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Add entry</h3>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="label">What did you learn? *</label>
              <textarea
                className="input resize-none"
                rows={3}
                required
                value={form.summary}
                onChange={(e) => setForm({ ...form, summary: e.target.value })}
                placeholder="e.g. Learned about SQLAlchemy lazy vs eager loading. Using selectinload() avoids N+1 in list queries."
              />
            </div>
            <div className="flex items-end gap-3">
              <div>
                <label className="label">Date</label>
                <input
                  type="date"
                  className="input w-40"
                  value={form.date}
                  onChange={(e) => setForm({ ...form, date: e.target.value })}
                />
              </div>
              <button type="submit" className="btn-primary" disabled={createLog.isPending}>
                {createLog.isPending ? "Saving…" : "Add entry"}
              </button>
            </div>
          </form>
        </div>

        {/* Entries list */}
        {isLoading ? (
          <div className="flex justify-center py-10"><Spinner /></div>
        ) : entries.length === 0 ? (
          <EmptyState
            icon={BookOpen}
            title="No entries yet"
            description="Start logging what you learn as you build."
          />
        ) : (
          <div className="space-y-3">
            {entries.map((entry) => (
              <EntryCard key={entry.id} entry={entry} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EntryCard({
  entry, onDelete,
}: {
  entry: LearningLog;
  onDelete: (id: number) => void;
}) {
  return (
    <div className="card px-5 py-4 flex gap-4 group">
      <div className="w-8 h-8 rounded-full bg-brand-50 flex items-center justify-center shrink-0 mt-0.5">
        <BookOpen size={14} className="text-brand-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{entry.summary}</p>
        <p className="text-xs text-gray-400 mt-1">
          {format(new Date(entry.date), "MMM d, yyyy")}
        </p>
      </div>
      <button
        onClick={() => onDelete(entry.id)}
        className="opacity-0 group-hover:opacity-100 p-1.5 rounded hover:text-red-500 text-gray-300 transition-all self-start"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}
