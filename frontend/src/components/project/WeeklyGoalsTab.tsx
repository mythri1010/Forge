"use client";

import { useState } from "react";
import toast from "react-hot-toast";
import { useWeeklyGoals, useCreateGoal, useReflections, useSubmitReflection } from "@/hooks/api/useWeekly";
import { WeeklyGoal } from "@/types";
import { Spinner } from "@/components/ui/Spinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { getErrorMessage } from "@/lib/api";
import { CheckCircle2, XCircle, ChevronDown, ChevronUp, Target } from "lucide-react";
import { format, startOfWeek } from "date-fns";
import clsx from "clsx";

interface Props { projectId: number }

export function WeeklyGoalsTab({ projectId }: Props) {
  const { data, isLoading } = useWeeklyGoals(projectId);
  const createGoal = useCreateGoal(projectId);
  const [form, setForm] = useState({
    goal_text: "",
    week_start_date: format(startOfWeek(new Date(), { weekStartsOn: 1 }), "yyyy-MM-dd"),
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.goal_text.trim()) return;
    try {
      await createGoal.mutateAsync(form);
      toast.success("Goal added");
      setForm({ ...form, goal_text: "" });
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  const goals = data?.items ?? [];

  return (
    <div className="p-6 space-y-5">
      {/* Add goal form */}
      <div className="card p-4">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Add goal for this week</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-3">
            <div className="flex-1">
              <label className="label">Week of</label>
              <input
                type="date"
                className="input"
                value={form.week_start_date}
                onChange={(e) => setForm({ ...form, week_start_date: e.target.value })}
              />
            </div>
          </div>
          <div>
            <label className="label">Goal *</label>
            <textarea
              className="input resize-none"
              rows={2}
              required
              value={form.goal_text}
              onChange={(e) => setForm({ ...form, goal_text: e.target.value })}
              placeholder="What does the team aim to ship this week?"
            />
          </div>
          <div className="flex justify-end">
            <button type="submit" className="btn-primary" disabled={createGoal.isPending}>
              {createGoal.isPending ? "Saving…" : "Add goal"}
            </button>
          </div>
        </form>
      </div>

      {/* Goals history */}
      {isLoading ? (
        <div className="flex justify-center py-10"><Spinner /></div>
      ) : goals.length === 0 ? (
        <EmptyState icon={Target} title="No weekly goals yet" description="Add your first goal above." />
      ) : (
        <div className="space-y-3">
          {goals.map((goal) => (
            <GoalCard key={goal.id} goal={goal} projectId={projectId} />
          ))}
        </div>
      )}
    </div>
  );
}

function GoalCard({ goal, projectId }: { goal: WeeklyGoal; projectId: number }) {
  const [expanded, setExpanded] = useState(false);
  const [showReflectForm, setShowReflectForm] = useState(false);
  const { data: reflections } = useReflections(goal.id);
  const submitReflection = useSubmitReflection(goal.id, projectId);
  const [reflectForm, setReflectForm] = useState({
    met_goal: true,
    blockers: "",
    process_notes: "",
    perceived_helpfulness: 4,
  });

  async function handleReflect(e: React.FormEvent) {
    e.preventDefault();
    try {
      await submitReflection.mutateAsync({
        met_goal: reflectForm.met_goal,
        blockers: reflectForm.blockers || undefined,
        process_notes: reflectForm.process_notes || undefined,
        perceived_helpfulness: reflectForm.perceived_helpfulness,
      });
      toast.success("Reflection saved");
      setShowReflectForm(false);
    } catch (err) {
      toast.error(getErrorMessage(err));
    }
  }

  const hasReflection = (reflections?.length ?? 0) > 0;
  const latestReflection = reflections?.[0];

  return (
    <div className="card">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-start gap-3 w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors rounded-xl"
      >
        <div className="mt-0.5 shrink-0">
          {hasReflection ? (
            latestReflection?.met_goal
              ? <CheckCircle2 size={18} className="text-green-500" />
              : <XCircle size={18} className="text-red-400" />
          ) : (
            <div className="w-[18px] h-[18px] rounded-full border-2 border-gray-300" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">
              Week of {format(new Date(goal.week_start_date), "MMM d, yyyy")}
            </span>
            {hasReflection && (
              <span className={clsx(
                "badge",
                latestReflection?.met_goal ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"
              )}>
                {latestReflection?.met_goal ? "Met" : "Not met"}
              </span>
            )}
          </div>
          <p className="text-sm font-medium text-gray-800 mt-0.5 line-clamp-2">{goal.goal_text}</p>
        </div>
        {expanded ? <ChevronUp size={16} className="text-gray-400 shrink-0 mt-1" /> : <ChevronDown size={16} className="text-gray-400 shrink-0 mt-1" />}
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-100 pt-3 space-y-3">
          {/* Reflections */}
          {hasReflection ? (
            <div className="space-y-2">
              {reflections?.map((r) => (
                <div key={r.id} className="bg-gray-50 rounded-lg p-3 text-xs space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-700">
                      {r.met_goal ? "✅ Goal met" : "❌ Goal not met"}
                    </span>
                    {r.perceived_helpfulness != null && (
                      <span className="text-gray-400">· Helpfulness: {r.perceived_helpfulness}/5</span>
                    )}
                  </div>
                  {r.blockers && <p className="text-gray-600"><span className="font-medium">Blockers:</span> {r.blockers}</p>}
                  {r.process_notes && <p className="text-gray-600"><span className="font-medium">Notes:</span> {r.process_notes}</p>}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-gray-400">No reflection submitted yet.</p>
          )}

          {/* Reflect button / form */}
          {!showReflectForm ? (
            <button className="btn-secondary text-xs py-1" onClick={() => setShowReflectForm(true)}>
              + Add reflection
            </button>
          ) : (
            <form onSubmit={handleReflect} className="bg-gray-50 rounded-lg p-3 space-y-3">
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-1.5 text-sm cursor-pointer">
                  <input
                    type="radio"
                    checked={reflectForm.met_goal}
                    onChange={() => setReflectForm({ ...reflectForm, met_goal: true })}
                  />
                  Goal met ✅
                </label>
                <label className="flex items-center gap-1.5 text-sm cursor-pointer">
                  <input
                    type="radio"
                    checked={!reflectForm.met_goal}
                    onChange={() => setReflectForm({ ...reflectForm, met_goal: false })}
                  />
                  Not met ❌
                </label>
              </div>
              <div>
                <label className="label text-xs">Blockers</label>
                <input
                  className="input text-sm"
                  value={reflectForm.blockers}
                  onChange={(e) => setReflectForm({ ...reflectForm, blockers: e.target.value })}
                  placeholder="Any blockers that prevented completion?"
                />
              </div>
              <div>
                <label className="label text-xs">Process notes</label>
                <input
                  className="input text-sm"
                  value={reflectForm.process_notes}
                  onChange={(e) => setReflectForm({ ...reflectForm, process_notes: e.target.value })}
                  placeholder="What went well / what to improve?"
                />
              </div>
              <div>
                <label className="label text-xs">Team helpfulness (1–5)</label>
                <input
                  type="range"
                  min={1} max={5}
                  value={reflectForm.perceived_helpfulness}
                  onChange={(e) => setReflectForm({ ...reflectForm, perceived_helpfulness: parseInt(e.target.value) })}
                  className="w-full accent-brand-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                  <span>1 – Not helpful</span>
                  <span className="font-medium text-gray-600">{reflectForm.perceived_helpfulness}</span>
                  <span>5 – Very helpful</span>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button type="button" className="btn-secondary text-xs py-1" onClick={() => setShowReflectForm(false)}>Cancel</button>
                <button type="submit" className="btn-primary text-xs py-1" disabled={submitReflection.isPending}>
                  {submitReflection.isPending ? "Saving…" : "Submit"}
                </button>
              </div>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
