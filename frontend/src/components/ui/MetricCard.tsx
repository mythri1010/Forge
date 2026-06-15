import clsx from "clsx";
import { Spinner } from "./Spinner";

interface MetricCardProps {
  label: string;
  value: string | number | null | undefined;
  sub?: string;
  accent?: "default" | "green" | "yellow" | "red" | "blue";
  loading?: boolean;
}

const accents = {
  default: "text-gray-900",
  green:   "text-green-600",
  yellow:  "text-yellow-600",
  red:     "text-red-600",
  blue:    "text-brand-600",
};

export function MetricCard({ label, value, sub, accent = "default", loading }: MetricCardProps) {
  return (
    <div className="card px-5 py-4">
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">{label}</p>
      {loading ? (
        <div className="mt-2"><Spinner size="sm" /></div>
      ) : (
        <p className={clsx("mt-1 text-2xl font-bold", accents[accent])}>
          {value ?? "—"}
        </p>
      )}
      {sub && <p className="mt-0.5 text-xs text-gray-400">{sub}</p>}
    </div>
  );
}
