"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { TeamMetrics } from "@/types";
import { Spinner } from "@/components/ui/Spinner";

interface Props {
  metrics?: TeamMetrics;
  loading?: boolean;
}

export function ThroughputChart({ metrics, loading }: Props) {
  if (loading) return <div className="flex justify-center py-8"><Spinner /></div>;

  // Build a simple per-member bar from the member stats
  const data = (metrics?.member_stats ?? []).map((m) => ({
    name: m.user_name.split(" ")[0],
    done: m.tasks_done_last_7d,
    hours: parseFloat(m.total_hours_last_7d.toFixed(1)),
  }));

  if (data.length === 0) {
    return <p className="text-xs text-gray-400 text-center py-8">No data yet</p>;
  }

  return (
    <div>
      <p className="text-xs text-gray-500 mb-3">Tasks done — last 7 days</p>
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data} margin={{ left: -20, right: 4, top: 4, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ fontSize: 12 }}
            formatter={(v: number, name: string) =>
              name === "hours" ? [`${v}h`, "Hours"] : [v, "Tasks done"]
            }
          />
          <Bar dataKey="done" fill="#6366f1" radius={[3, 3, 0, 0]} name="done" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
