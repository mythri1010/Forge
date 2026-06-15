"use client";

import { useProjectMetrics } from "@/hooks/api/useProjects";
import { MetricCard } from "@/components/ui/MetricCard";
import { Spinner } from "@/components/ui/Spinner";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";

interface Props { projectId: number }

const STATUS_COLORS: Record<string, string> = {
  TODO: "#9ca3af",
  IN_PROGRESS: "#6366f1",
  IN_REVIEW: "#a855f7",
  BLOCKED: "#ef4444",
};

export function AnalyticsTab({ projectId }: Props) {
  const { data: metrics, isLoading } = useProjectMetrics(projectId);

  if (isLoading) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  }

  const wipData = Object.entries(metrics?.wip_by_status ?? {}).map(([status, count]) => ({
    status: status.replace(/_/g, " "),
    rawStatus: status,
    count,
  }));

  const healthScore = metrics?.health_score ?? 0;
  const healthAccent =
    healthScore >= 70 ? "green" : healthScore >= 40 ? "yellow" : "red";

  return (
    <div className="p-6 space-y-6">
      {/* Key metric cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Avg lead time"
          value={metrics?.avg_lead_time_days != null ? `${metrics.avg_lead_time_days.toFixed(1)}d` : null}
          sub="created → done"
        />
        <MetricCard
          label="Avg cycle time"
          value={metrics?.avg_cycle_time_days != null ? `${metrics.avg_cycle_time_days.toFixed(1)}d` : null}
          sub="in-progress → done"
          accent="blue"
        />
        <MetricCard
          label="Throughput"
          value={metrics?.throughput_per_week}
          sub="tasks done / week"
          accent="green"
        />
        <MetricCard
          label="Health score"
          value={metrics?.health_score != null ? `${metrics.health_score}/100` : null}
          sub={metrics?.tasks_at_risk_count ? `${metrics.tasks_at_risk_count} tasks at risk` : "All on track"}
          accent={healthAccent}
        />
      </div>

      {/* WIP by status chart */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-4">Work in progress by status</h3>
        {wipData.length === 0 ? (
          <p className="text-xs text-gray-400 text-center py-8">No open tasks</p>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={wipData} margin={{ left: -16, right: 8, top: 4, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="status" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
              <Tooltip contentStyle={{ fontSize: 12 }} formatter={(v) => [v, "Tasks"]} />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {wipData.map((entry) => (
                  <Cell
                    key={entry.rawStatus}
                    fill={STATUS_COLORS[entry.rawStatus] ?? "#6366f1"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Tasks at risk callout */}
      {(metrics?.tasks_at_risk_count ?? 0) > 0 && (
        <div className="rounded-lg bg-red-50 border border-red-200 px-4 py-3">
          <p className="text-sm font-medium text-red-700">
            ⚠️ {metrics!.tasks_at_risk_count} task{metrics!.tasks_at_risk_count !== 1 ? "s are" : " is"} past due and not done.
          </p>
          <p className="text-xs text-red-500 mt-0.5">
            Review the List tab and update due dates or status.
          </p>
        </div>
      )}
    </div>
  );
}
