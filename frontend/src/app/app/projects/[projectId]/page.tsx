"use client";

import { use, useState } from "react";
import { Header } from "@/components/layout/Header";
import { Tabs } from "@/components/ui/Tabs";
import { Spinner } from "@/components/ui/Spinner";
import { useProject } from "@/hooks/api/useProjects";
import { KanbanBoard } from "@/components/project/KanbanBoard";
import { TaskListTab } from "@/components/project/TaskListTab";
import { AnalyticsTab } from "@/components/project/AnalyticsTab";
import { WeeklyGoalsTab } from "@/components/project/WeeklyGoalsTab";

const TABS = [
  { id: "board",   label: "Board" },
  { id: "list",    label: "List" },
  { id: "analytics", label: "Analytics" },
  { id: "weekly", label: "Weekly Goals" },
];

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ projectId: string }>;
}) {
  const { projectId } = use(params);
  const id = parseInt(projectId, 10);
  const { data: project, isLoading } = useProject(id);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <Header title={project?.name ?? "Project"} />
      <div className="flex-1 overflow-hidden">
        <Tabs tabs={TABS}>
          {(active) => {
            if (active === "board")     return <KanbanBoard projectId={id} />;
            if (active === "list")      return <TaskListTab projectId={id} />;
            if (active === "analytics") return <AnalyticsTab projectId={id} />;
            if (active === "weekly")    return <WeeklyGoalsTab projectId={id} />;
            return null;
          }}
        </Tabs>
      </div>
    </div>
  );
}
