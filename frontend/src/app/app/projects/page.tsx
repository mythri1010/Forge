"use client";

import { useState } from "react";
import Link from "next/link";
import toast from "react-hot-toast";
import { Header } from "@/components/layout/Header";
import { Modal } from "@/components/ui/Modal";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useProjects, useCreateProject, useProjectMetrics } from "@/hooks/api/useProjects";
import { getErrorMessage } from "@/lib/api";
import { Project, ProjectMetrics } from "@/types";
import { FolderKanban, Plus, ChevronRight } from "lucide-react";
import clsx from "clsx";

function healthColor(score: number | undefined) {
  if (score == null) return "bg-gray-200 text-gray-500";
  if (score >= 70) return "bg-green-100 text-green-700";
  if (score >= 40) return "bg-yellow-100 text-yellow-700";
  return "bg-red-100 text-red-700";
}

function healthLabel(score: number | undefined) {
  if (score == null) return "—";
  if (score >= 70) return "Healthy";
  if (score >= 40) return "At risk";
  return "Critical";
}

function ProjectRow({ project }: { project: Project }) {
  const { data: metrics } = useProjectMetrics(project.id);
  return (
    <Link
      href={`/app/projects/${project.id}`}
      className="flex items-center gap-4 px-5 py-4 hover:bg-gray-50 transition-colors"
    >
      <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center shrink-0">
        <FolderKanban size={16} className="text-brand-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900">{project.name}</p>
        {project.description && (
          <p className="text-xs text-gray-400 truncate mt-0.5">{project.description}</p>
        )}
      </div>
      <ProjectMetaChips metrics={metrics} />
      <ChevronRight size={14} className="text-gray-300 shrink-0" />
    </Link>
  );
}

function ProjectMetaChips({ metrics }: { metrics?: ProjectMetrics }) {
  return (
    <div className="flex items-center gap-2 shrink-0">
      <span className="text-xs text-gray-500">
        {metrics ? `${metrics.throughput_per_week} done / week` : "—"}
      </span>
      <span
        className={clsx(
          "badge",
          healthColor(metrics?.health_score)
        )}
      >
        {healthLabel(metrics?.health_score)}
      </span>
    </div>
  );
}

function CreateProjectModal({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const create = useCreateProject();
  const [form, setForm] = useState({
    name: "",
    description: "",
    start_date: "",
    end_date: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await create.mutateAsync({
        name: form.name,
        description: form.description || undefined,
        start_date: form.start_date || undefined,
        end_date: form.end_date || undefined,
      });
      toast.success("Project created");
      onClose();
      setForm({ name: "", description: "", start_date: "", end_date: "" });
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="New project">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="label">Project name *</label>
          <input
            className="input"
            required
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="e.g. Inventory Management System"
          />
        </div>
        <div>
          <label className="label">Description</label>
          <textarea
            className="input resize-none"
            rows={3}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Start date</label>
            <input
              type="date"
              className="input"
              value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            />
          </div>
          <div>
            <label className="label">End date</label>
            <input
              type="date"
              className="input"
              value={form.end_date}
              onChange={(e) => setForm({ ...form, end_date: e.target.value })}
            />
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <button type="button" className="btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" className="btn-primary" disabled={create.isPending}>
            {create.isPending ? "Creating…" : "Create project"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

export default function ProjectsPage() {
  const { data, isLoading } = useProjects();
  const [creating, setCreating] = useState(false);

  return (
    <div className="flex flex-col h-full">
      <Header
        title="Projects"
        actions={
          <button className="btn-primary" onClick={() => setCreating(true)}>
            <Plus size={15} />
            New project
          </button>
        }
      />

      <div className="flex-1 p-6 overflow-y-auto">
        {isLoading ? (
          <div className="flex justify-center py-20"><Spinner size="lg" /></div>
        ) : !data?.items?.length ? (
          <div className="card">
            <EmptyState
              icon={FolderKanban}
              title="No projects yet"
              description="Create your first project to start tracking tasks."
              action={
                <button className="btn-primary" onClick={() => setCreating(true)}>
                  <Plus size={15} /> New project
                </button>
              }
            />
          </div>
        ) : (
          <div className="card divide-y divide-gray-100">
            {data.items.map((p) => (
              <ProjectRow key={p.id} project={p} />
            ))}
          </div>
        )}
      </div>

      <CreateProjectModal open={creating} onClose={() => setCreating(false)} />
    </div>
  );
}
