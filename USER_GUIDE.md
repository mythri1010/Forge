# Project Tracker - User Guide

A comprehensive guide to using the Project Tracker application for team collaboration and project management.

---

## Table of Contents

1. Getting Started
2. Account Setup
3. Team Management
4. Projects
5. Tasks & Kanban Board
6. Time Logging
7. Weekly Goals & Reflections
8. Learning Log
9. Analytics & Metrics
10. Admin Features
11. Tips & Best Practices

---

## 1. Getting Started

### Accessing the App

Open your browser and navigate to your deployed app URL (e.g., `https://your-app.vercel.app`).

### First Time Setup

1. You'll be redirected to the login page
2. Click "Register" to create a new account
3. Fill in your name, email, and password
4. After registration, you're automatically logged in

---

## 2. Account Setup

### Registration

Required fields:
- Name: Your full name
- Email: Must be unique across the platform
- Password: Minimum 8 characters

### Login

Use your email and password to sign in. Your session persists across browser refreshes.

---

## 3. Team Management

### Creating a Team

When you first log in, you won't be part of any team.

1. Navigate to the "Team" page from the sidebar
2. Click "Create New Team"
3. Enter your team name
4. You automatically become the Team Admin
5. An invite code is generated (e.g., `ABC123`)

### Joining a Team

If someone else created a team:

1. Go to the "Team" page
2. Click "Join Existing Team"
3. Enter the invite code shared by your team admin
4. You join as a regular team member

### Team Page Features

- View team name and invite code
- Copy invite code to clipboard (click the copy icon)
- See all team members with their roles
- Team admins can update member roles

### Roles

- USER: Regular team member, can create projects and tasks
- TEAM_ADMIN: Can update projects and manage team member roles
- PLATFORM_ADMIN: Full access to admin dashboard (requires database update)

---

## 4. Projects

### Viewing Projects

1. Click "Projects" in the sidebar
2. See all projects belonging to your team
3. Each project shows:
   - Project name and description
   - Start and end dates (if set)
   - Health score indicator (green/yellow/red)

### Creating a Project

1. On the Projects page, click "New Project"
2. Fill in:
   - Name (required)
   - Description (optional)
   - Start date (optional)
   - End date (optional)
3. Click "Create Project"

### Project Health Indicator

Projects display a colored indicator based on their health score:
- Green (80-100): Healthy, on track
- Yellow (50-79): Needs attention
- Red (0-49): At risk

Health is calculated from:
- Percentage of completed tasks
- Number of overdue tasks
- Work in progress levels

---

## 5. Tasks & Kanban Board

### Viewing Tasks

Click on any project to open its detail page with multiple tabs:
- Kanban Board (default view)
- Task List
- Analytics
- Weekly Goals

### Kanban Board

The board has 5 columns:
- TODO: New tasks, not started
- IN PROGRESS: Currently being worked on
- IN REVIEW: Awaiting review
- BLOCKED: Stuck, needs help
- DONE: Completed

### Creating Tasks

Method 1 - From Kanban:
1. Click the "+" button on any column header
2. Enter task title
3. Task is created in that status

Method 2 - From Task List:
1. Switch to "Task List" tab
2. Click "New Task"
3. Fill in all details

### Task Details

Each task has:
- Title (required)
- Description (optional)
- Status (TODO, IN PROGRESS, IN REVIEW, BLOCKED, DONE)
- Priority (LOW, MEDIUM, HIGH, CRITICAL)
- Assignee (any team member)
- Due date (optional)
- Created date (automatic)
- Completed date (automatic when moved to DONE)

### Moving Tasks

Drag and drop tasks between columns on the Kanban board, or use the status dropdown in the task drawer.

### Task Drawer

Click any task card to open the detail drawer:
- View and edit all task fields
- See status history (who changed status and when)
- Log time worked
- View all time entries
- See creation and completion timestamps

### Filtering Tasks

On the Task List tab:
- Filter by status
- Filter by assignee
- Sort by various fields

---

## 6. Time Logging

### Logging Time on a Task

1. Open a task in the drawer
2. Scroll to the "Time Logged" section
3. Click "Log Time"
4. Fill in:
   - Date (defaults to today)
   - Hours (0.1 to 24)
   - Note (optional)
5. Click "Save"

### Viewing Time Logs

- See all time entries for a task in the task drawer
- Each entry shows date, hours, note, and who logged it
- Delete your own time entries (trash icon)

### My Tasks Page

View all tasks assigned to you:
- Active tasks with inline status controls
- Recently completed tasks
- Personal metrics:
  - Current work in progress
  - Hours logged this week
  - Tasks completed this week
  - Average cycle time
- Bar chart of hours logged per day

---

## 7. Weekly Goals & Reflections

### Setting Weekly Goals

1. Open a project
2. Go to the "Weekly Goals" tab
3. Click "Add Goal for This Week"
4. Enter your goal statement
5. The goal is tied to the current calendar week

### Submitting Reflections

At the end of the week:
1. Find the goal for that week
2. Click "Add Reflection"
3. Fill in:
   - Did you meet the goal? (Yes/No)
   - Blockers encountered (optional)
   - Process notes (optional)
   - Helpfulness score (1-5 slider)
4. Submit

### Viewing Past Goals

All goals are listed chronologically. Expand any goal to see its reflections.

---

## 8. Learning Log

Your personal journal for capturing learnings.

### Accessing Learning Log

Click "Me" in the sidebar, then "Learning Log".

### Adding an Entry

1. Click "Add Entry"
2. Fill in:
   - Date (defaults to today)
   - What did you learn? (text)
   - Related task (optional dropdown)
3. Click "Save"

### Viewing Entries

All entries are listed chronologically, newest first. Each shows:
- Date
- Learning summary
- Related task (if linked)

### Exporting

Click "Export as JSON" to copy all your entries to the clipboard.

---

## 9. Analytics & Metrics

### Dashboard Metrics

The main dashboard shows:
- Your current work in progress
- Hours logged this week
- Tasks completed this week
- Your average cycle time
- Active tasks with status controls
- Team throughput chart (tasks and hours per member)

### Project Analytics

Open any project and go to the "Analytics" tab:

Metrics displayed:
- Average Lead Time: Days from task creation to completion
- Average Cycle Time: Days from "In Progress" to "Done"
- Throughput: Tasks completed in last 7 days
- Health Score: 0-100 overall project health
- WIP by Status: Bar chart showing work distribution
- Tasks at Risk: Count of overdue tasks

If tasks are overdue, a warning banner appears.

### Team Metrics

On the dashboard, see per-member stats:
- Current WIP
- Tasks done (last 7 days)
- Hours logged (last 7 days)
- Average cycle time

---

## 10. Admin Features

### Accessing Admin Dashboard

Admin access requires the `PLATFORM_ADMIN` role. This must be set directly in the database:

```sql
UPDATE users SET role = 'PLATFORM_ADMIN' WHERE email = 'your@email.com';
```

Once set, the "Admin" section appears in the sidebar.

### Admin Overview

The admin dashboard shows:
- Platform-wide activity chart (hours and tasks per week)
- Team overview table with:
  - Team name
  - User count
  - Project and task counts
  - Total hours logged
  - Last activity date
  - Weekly goal success rate
  - Average helpfulness score

### Feedback Management

Admin → Feedback:
- View all feedback from all teams
- Filter by status (OPEN, REVIEWED, CLOSED)
- Filter by category
- Update feedback status
- See which team submitted each item

---

## 11. Tips & Best Practices

### For Team Admins

1. Share the invite code via secure channels
2. Set clear project start and end dates
3. Review team metrics weekly
4. Encourage weekly goal setting
5. Monitor health scores and address red projects

### For Team Members

1. Keep tasks small and focused
2. Update task status regularly
3. Log time daily for accuracy
4. Use priority levels effectively:
   - CRITICAL: Urgent, blocking others
   - HIGH: Important, time-sensitive
   - MEDIUM: Normal priority
   - LOW: Nice to have, not urgent
5. Add notes to time logs for context
6. Link learning log entries to tasks

### Task Management

1. Move tasks to IN PROGRESS only when actively working
2. Use BLOCKED status when stuck
3. Add assignees to clarify ownership
4. Set due dates for time-sensitive work
5. Use descriptions for context and acceptance criteria

### Weekly Goals

1. Make goals specific and measurable
2. Set one clear goal per week per project
3. Submit reflections honestly
4. Use blockers field to identify patterns
5. Rate helpfulness to improve the process

### Time Tracking

1. Log time daily, not weekly
2. Be honest about hours
3. Use notes to explain what was done
4. Round to nearest 0.5 hours for simplicity
5. Don't log more than 24 hours per day

### Analytics

1. Check project health scores weekly
2. Address high WIP (work in progress)
3. Investigate long cycle times
4. Celebrate high throughput
5. Use metrics to identify bottlenecks

---

## Keyboard Shortcuts

- Click task cards to open details
- Drag tasks to move between statuses
- Use Tab to navigate forms
- Enter to submit forms
- Escape to close modals

---

## Troubleshooting

### Can't see projects
- Make sure you've joined or created a team first

### Can't edit a project
- Only Team Admins can update project details

### Task won't move to DONE
- Check if all required fields are filled

### Time log rejected
- Hours must be between 0.1 and 24
- Date cannot be in the future

### Invite code not working
- Codes are case-sensitive
- Make sure you're not already in a team
- Ask the team admin to verify the code

---

## Support

For issues or questions:
1. Check this guide first
2. Review the README.md for technical setup
3. Contact your platform administrator
4. Submit feedback via the app (if available)

---

## API Documentation

For developers, the interactive API docs are available at:
```
http://localhost:5000/api/docs (local)
https://your-backend.onrender.com/api/docs (production)
```
