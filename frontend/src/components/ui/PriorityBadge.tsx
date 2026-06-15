import { TaskPriority } from "@/types";
import clsx from "clsx";

const styles: Record<TaskPriority, string> = {
  LOW:      "bg-gray-100 text-gray-500",
  MEDIUM:   "bg-yellow-100 text-yellow-700",
  HIGH:     "bg-orange-100 text-orange-700",
  CRITICAL: "bg-red-100 text-red-700",
};

export function PriorityBadge({ priority }: { priority: TaskPriority }) {
  return (
    <span className={clsx("badge", styles[priority])}>
      {priority.charAt(0) + priority.slice(1).toLowerCase()}
    </span>
  );
}
