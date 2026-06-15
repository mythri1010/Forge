"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FolderKanban,
  CheckSquare,
  BookOpen,
  ShieldCheck,
  MessageSquare,
  LogOut,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import clsx from "clsx";

const navItems = [
  { href: "/app/dashboard",        label: "Dashboard",    icon: LayoutDashboard },
  { href: "/app/projects",         label: "Projects",     icon: FolderKanban },
  { href: "/app/my-tasks",         label: "My Tasks",     icon: CheckSquare },
  { href: "/app/me/learning-log",  label: "Learning Log", icon: BookOpen },
];

const adminItems = [
  { href: "/admin",          label: "Overview",  icon: ShieldCheck },
  { href: "/admin/feedback", label: "Feedback",  icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout, isAdmin } = useAuth();

  return (
    <aside className="flex flex-col w-60 min-h-screen bg-white border-r border-gray-200 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-4 border-b border-gray-100">
        <div className="w-7 h-7 rounded-md bg-brand-600 flex items-center justify-center">
          <span className="text-white text-xs font-bold">PT</span>
        </div>
        <span className="font-semibold text-gray-900 text-sm">Project Tracker</span>
      </div>

      {/* Main nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => (
          <NavLink key={href} href={href} label={label} icon={Icon} active={pathname.startsWith(href)} />
        ))}

        {isAdmin && (
          <>
            <div className="mt-4 mb-2 px-2">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                Platform Admin
              </p>
            </div>
            {adminItems.map(({ href, label, icon: Icon }) => (
              <NavLink key={href} href={href} label={label} icon={Icon} active={pathname.startsWith(href)} />
            ))}
          </>
        )}
      </nav>

      {/* User footer */}
      <div className="px-3 py-3 border-t border-gray-100">
        <div className="flex items-center gap-2 px-2 py-2 rounded-md">
          <div className="w-7 h-7 rounded-full bg-brand-100 flex items-center justify-center shrink-0">
            <span className="text-brand-700 text-xs font-semibold">
              {user?.role?.charAt(0) ?? "U"}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-gray-800 truncate">
              {user?.role?.replace(/_/g, " ")}
            </p>
            <p className="text-[11px] text-gray-400">ID {user?.user_id}</p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
            title="Sign out"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </aside>
  );
}

function NavLink({
  href,
  label,
  icon: Icon,
  active,
}: {
  href: string;
  label: string;
  icon: React.ElementType;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={clsx(
        "flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm transition-colors",
        active
          ? "bg-brand-50 text-brand-700 font-medium"
          : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
      )}
    >
      <Icon size={16} strokeWidth={active ? 2.5 : 2} />
      {label}
    </Link>
  );
}
