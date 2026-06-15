import { TaskStatus } from "@/types";
import clsx from "clsx";

const styles: Record<TaskStatus, string> = {
  TODO:        "bg-gray-100 text-gray-600",
  IN_PROGRESS: "bg-blue-100 text-blue-700",
  IN_REVIEW:   "bg-purple-100 text-purple-700",
  BLOCKED:     "bg-red-100 text-red-700",
  DONE:        "bg-green-100 text-green-700",
};

const labels: Record<TaskStatus, string> = {
  TODO:        "To Do",
  IN_PROGRESS: "In Progress",
  IN_REVIEW:   "In Review",
  BLOCKED:     "Blocked",
  DONE:        "Done",
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span className={clsx("badge", styles[status])}>
      {labels[status]}
    </span>
  );
}
