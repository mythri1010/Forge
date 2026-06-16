"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { Header } from "@/components/layout/Header";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAdminFeedback, useUpdateFeedbackStatus } from "@/hooks/api/useAdmin";
import { Feedback } from "@/types";
import { getErrorMessage } from "@/lib/api";
import { MessageSquare } from "lucide-react";
import { format } from "date-fns";
import clsx from "clsx";

const STATUS_STYLES: Record<string, string> = {
  OPEN:     "bg-blue-100 text-blue-700",
  REVIEWED: "bg-yellow-100 text-yellow-700",
  CLOSED:   "bg-gray-100 text-gray-500",
};

const CATEGORY_STYLES: Record<string, string> = {
  BUG:     "bg-red-100 text-red-600",
  FEATURE: "bg-purple-100 text-purple-700",
  GENERAL: "bg-gray-100 text-gray-600",
};

export default function AdminFeedbackPage() {
  const { data: feedback, isLoading } = useAdminFeedback();
  const updateStatus = useUpdateFeedbackStatus();
  const [filterStatus, setFilterStatus] = useState("");
  const [filterCategory, setFilterCategory] = useState("");

  const entries = (feedback ?? []).filter((f) => {
    if (filterStatus && f.status !== filterStatus) return false;
    if (filterCategory && f.category !== filterCategory) return false;
    return true;
  });

  async function handleStatusChange(id: number, status: string) {
    try {
      await updateStatus.mutateAsync({ id, status });
      toast.success("Status updated");
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <div className="flex flex-col h-full">
      <Header title="Feedback" />
      <div className="flex-1 p-6 space-y-4 overflow-y-auto">

        {/* Filters */}
        <div className="flex gap-3">
          <select
            className="input w-36"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="">All statuses</option>
            <option value="OPEN">Open</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="CLOSED">Closed</option>
          </select>
          <select
            className="input w-36"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="">All categories</option>
            <option value="BUG">Bug</option>
            <option value="FEATURE">Feature</option>
            <option value="GENERAL">General</option>
          </select>
          <span className="text-xs text-gray-400 self-center ml-auto">
            {entries.length} item{entries.length !== 1 ? "s" : ""}
          </span>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20"><Spinner size="lg" /></div>
        ) : entries.length === 0 ? (
          <EmptyState icon={MessageSquare} title="No feedback matches filters" />
        ) : (
          <div className="space-y-3">
            {entries.map((f) => (
              <FeedbackCard key={f.id} feedback={f} onStatusChange={handleStatusChange} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function FeedbackCard({
  feedback: f,
  onStatusChange,
}: {
  feedback: Feedback;
  onStatusChange: (id: number, status: string) => void;
}) {
  return (
    <div className="card px-5 py-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5">
            <span className={clsx("badge", CATEGORY_STYLES[f.category] ?? "bg-gray-100 text-gray-600")}>
              {f.category}
            </span>
            <span className={clsx("badge", STATUS_STYLES[f.status])}>
              {f.status}
            </span>
            <span className="text-xs text-gray-400">
              {f.team_name ?? `Team ${f.team_id}`}
            </span>
            <span className="text-xs text-gray-300">·</span>
            <span className="text-xs text-gray-400">
              {format(new Date(f.created_at), "MMM d, yyyy")}
            </span>
          </div>
          <p className="text-sm text-gray-800">{f.message}</p>
        </div>
        <select
          className="input w-32 shrink-0 text-xs"
          value={f.status}
          onChange={(e) => onStatusChange(f.id, e.target.value)}
        >
          <option value="OPEN">Open</option>
          <option value="REVIEWED">Reviewed</option>
          <option value="CLOSED">Closed</option>
        </select>
      </div>
    </div>
  );
}
