"use client";

import { useMyTeam } from "@/hooks/api/useTeam";

interface HeaderProps {
  title: string;
  actions?: React.ReactNode;
}

export function Header({ title, actions }: HeaderProps) {
  const { data: team } = useMyTeam();

  return (
    <header className="flex items-center justify-between h-14 px-6 border-b border-gray-200 bg-white shrink-0">
      <div className="flex items-center gap-3">
        <h1 className="text-base font-semibold text-gray-900">{title}</h1>
        {team && (
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
            {team.name}
          </span>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  );
}
