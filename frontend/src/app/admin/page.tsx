"use client";

import { useMemo } from "react";
import { Header } from "@/components/layout/Header";
import { Spinner } from "@/components/ui/Spinner";
import { useAdminOverview, useAdminTimeseries } from "@/hooks/api/useAdmin";
import { AdminTeamRow } from "@/types";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer, CartesianGrid,
} from "recharts";
import clsx from "clsx";

function healthColor(rate: number | null) {
  if (rate == null) return "text-gray-400";
  if (rate >= 0.7) return "text-green-600";
  if (rate >= 0.4) return "text-yellow-600";
  return "text-red-600";
}

export default function AdminOverviewPage() {
  const { data: teams, isLoading } = useAdminOverview();
  const { data: timeseries } = useAdminTimeseries(8);

  // Aggregate timeseries by week across all teams
  const chartData = useMemo(() => {
    if (!timeseries) return [];
    const byWeek: Record<string, { week: string; hours: number; tasks: number }> = {};
    for (const row of timeseries) {
      if (!byWeek[row.week]) byWeek[row.week] = { week: row.week, hours: 0, tasks: 0 };
      byWeek[row.week].hours += row.hours_logged;
      byWeek[row.week].tasks += row.tasks_completed;
    }
    return Object.values(byWeek).sort((a, b) => a.week.localeCompare(b.week));
  }, [timeseries]);

  return (
    <div className="flex flex-col h-full">
      <Header title="Platform Overview" />
      <div className="flex-1 p-6 space-y-6 overflow-y-auto">

        {/* Usage chart */}
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">
            Platform activity — last 8 weeks
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={chartData} margin={{ left: -16, right: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="week" tick={{ fontSize: 11 }} />
              <YAxis yAxisId="left" tick={{ fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ fontSize: 12 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar yAxisId="left" dataKey="hours" name="Hours logged" fill="#6366f1" radius={[3,3,0,0]} />
              <Bar yAxisId="right" dataKey="tasks" name="Tasks done" fill="#10b981" radius={[3,3,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Teams table */}
        {isLoading ? (
          <div className="flex justify-center py-10"><Spinner size="lg" /></div>
        ) : (
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  {["Team","Users","Projects","Tasks","Hours","Last active","Goal success","Helpfulness"].map((h) => (
                    <th key={h} className="text-left px-4 py-2.5 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {(teams ?? []).map((team) => (
                  <AdminTeamTableRow key={team.team_id} team={team} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function AdminTeamTableRow({ team }: { team: AdminTeamRow }) {
  const lastActive = team.last_active_at
    ? new Date(team.last_active_at).toLocaleDateString()
    : "—";

  const goalRate = team.avg_weekly_goal_success_rate;
  const helpfulness = team.avg_perceived_helpfulness;

  return (
    <tr className="hover:bg-gray-50 transition-colors">
      <td className="px-4 py-3 font-medium text-gray-900">{team.team_name}</td>
      <td className="px-4 py-3 text-gray-600">{team.user_count}</td>
      <td className="px-4 py-3 text-gray-600">{team.project_count}</td>
      <td className="px-4 py-3 text-gray-600">{team.task_count}</td>
      <td className="px-4 py-3 text-gray-600">{team.total_hours.toFixed(0)}h</td>
      <td className="px-4 py-3 text-gray-400 text-xs">{lastActive}</td>
      <td className={clsx("px-4 py-3 font-medium", healthColor(goalRate))}>
        {goalRate != null ? `${(goalRate * 100).toFixed(0)}%` : "—"}
      </td>
      <td className="px-4 py-3 text-gray-600">
        {helpfulness != null ? `${helpfulness.toFixed(1)} / 5` : "—"}
      </td>
    </tr>
  );
}
