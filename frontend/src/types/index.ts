// ── Auth ─────────────────────────────────────────────────────────────────────

export type Role = "USER" | "TEAM_ADMIN" | "PLATFORM_ADMIN";

export interface AuthUser {
  user_id: number;
  role: Role;
  team_id: number | null;
  access_token: string;
}

// ── Team ─────────────────────────────────────────────────────────────────────

export interface Team {
  id: number;
  name: string;
  invite_code: string;
  created_at: string;
}

export interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  user_name: string;
  user_email: string;
  role_in_team: "USER" | "TEAM_ADMIN";
  joined_at: string;
}

// ── Project ───────────────────────────────────────────────────────────────────

export interface Project {
  id: number;
  team_id: number;
  name: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  created_by: number;
  created_at: string;
}

// ── Task ─────────────────────────────────────────────────────────────────────

export type TaskStatus = "TODO" | "IN_PROGRESS" | "IN_REVIEW" | "DONE" | "BLOCKED";
export type TaskPriority = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface Task {
  id: number;
  project_id: number;
  team_id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  created_by: number;
  assignee_id: number | null;
  due_date: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface StatusHistory {
  id: number;
  task_id: number;
  from_status: TaskStatus | null;
  to_status: TaskStatus;
  changed_at: string;
  changed_by: number;
}

// ── Worklog ───────────────────────────────────────────────────────────────────

export interface Worklog {
  id: number;
  task_id: number;
  team_id: number;
  user_id: number;
  date: string;
  hours: number;
  note: string | null;
  created_at: string;
}

// ── Weekly ────────────────────────────────────────────────────────────────────

export interface WeeklyGoal {
  id: number;
  project_id: number;
  team_id: number;
  week_start_date: string;
  goal_text: string;
  created_at: string;
}

export interface WeeklyReflection {
  id: number;
  weekly_goal_id: number;
  met_goal: boolean;
  blockers: string | null;
  process_notes: string | null;
  perceived_helpfulness: number | null;
  created_at: string;
}

// ── Learning ──────────────────────────────────────────────────────────────────

export interface LearningLog {
  id: number;
  user_id: number;
  task_id: number | null;
  date: string;
  summary: string;
  created_at: string;
}

// ── Feedback ──────────────────────────────────────────────────────────────────

export interface Feedback {
  id: number;
  team_id: number;
  team_name?: string;
  user_id: number;
  category: string;
  message: string;
  status: "OPEN" | "REVIEWED" | "CLOSED";
  created_at: string;
}

// ── Analytics ─────────────────────────────────────────────────────────────────

export interface ProjectMetrics {
  project_id: number;
  avg_lead_time_days: number | null;
  avg_cycle_time_days: number | null;
  throughput_per_week: number;
  wip_by_status: Record<string, number>;
  tasks_at_risk_count: number;
  health_score: number;
}

export interface MemberStat {
  user_id: number;
  user_name: string;
  current_wip: number;
  tasks_done_last_7d: number;
  total_hours_last_7d: number;
  avg_cycle_time_days: number | null;
}

export interface TeamMetrics {
  team_id: number;
  member_stats: MemberStat[];
  weekly_goal_success_rate: number | null;
  avg_perceived_helpfulness: number | null;
}

export interface AdminTeamRow {
  team_id: number;
  team_name: string;
  user_count: number;
  project_count: number;
  task_count: number;
  total_hours: number;
  last_active_at: string | null;
  avg_weekly_goal_success_rate: number | null;
  avg_perceived_helpfulness: number | null;
}

export interface TimeseriesRow {
  week: string;
  team_id: number;
  worklog_count: number;
  hours_logged: number;
  tasks_completed: number;
}

// ── Pagination ────────────────────────────────────────────────────────────────

export interface Paginated<T> {
  items: T[];
  page: number;
  per_page: number;
  total: number;
  pages: number;
}
