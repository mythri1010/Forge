# Forge 🚀

Forge is a full-stack collaborative project management platform designed to help teams organize projects, manage tasks, track productivity, and monitor progress through analytics. It combines project planning, Kanban-based task management, time tracking, learning journals, weekly goals, and team collaboration into a single workspace.

---

# 📌 Features

## 👥 Team Management

- Create and manage teams
- Join teams using invite codes
- Team Admin role for team administration
- Team-based project collaboration

## 📁 Project Management

- Create and manage projects
- Set project descriptions and timelines
- Organize tasks within projects
- Track project progress

## ✅ Task Management

- Kanban Board workflow
- Create, edit, and delete tasks
- Assign tasks to team members
- Set due dates
- Track task progress

### Task Statuses

- TODO
- IN_PROGRESS
- IN_REVIEW
- BLOCKED
- DONE

### Task Priorities

- LOW
- MEDIUM
- HIGH
- CRITICAL

## ⏱️ Time Tracking

- Log hours worked on tasks
- Record work dates
- Add notes to work logs
- Monitor team productivity

## 🎯 Weekly Goals

- Set weekly objectives
- Submit end-of-week reflections
- Rate goal helpfulness
- Track personal and team progress

## 📋 My Tasks

- View all assigned tasks
- Update task statuses
- Track weekly work hours
- Monitor personal workload

## 📚 Learning Log

- Maintain a personal learning journal
- Link learning entries to tasks
- Record daily learnings
- Export entries as JSON

## 📊 Analytics Dashboard

- Lead Time Analysis
- Cycle Time Analysis
- Throughput Tracking
- Work-In-Progress (WIP) Monitoring
- Team Performance Metrics
- Project Health Score

## 🛠️ Admin Dashboard

Platform administrators can:

- Monitor platform activity
- View team statistics
- Manage user feedback
- Access platform-wide analytics

---

# 🏗️ Tech Stack

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- React Query

## Backend

- Flask
- SQLAlchemy
- Flask-Migrate
- Flask-JWT-Extended
- PostgreSQL

## DevOps & Tools

- Docker
- Docker Compose
- Swagger/OpenAPI
- Pytest

---

# 📂 Project Structure

```text
Forge/
├── backend/
│   ├── app/
│   │   ├── blueprints/
│   │   ├── models/
│   │   ├── utils/
│   │   ├── config.py
│   │   └── extensions.py
│   ├── tests/
│   ├── run.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   └── next.config.js
│
├── README.md
├── USER_GUIDE.md
└── DEPLOYMENT.md
```

---

# ⚙️ Prerequisites

Before running the project, ensure the following are installed:

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Git

---

# 🚀 Installation & Setup

## Backend Setup

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

flask db upgrade

python run.py
```

Backend will run at:

```text
http://localhost:5000
```

---

## Frontend Setup

```bash
cd frontend

npm install

cp .env.local.example .env.local

npm run dev
```

Frontend will run at:

```text
http://localhost:3000
```

---

# 🔐 Authentication

Forge provides:

- User Registration
- User Login
- JWT Authentication
- Session Management
- Protected Routes
- Role-Based Access Control

---

# 📖 API Documentation

When the backend is running, Swagger documentation is available at:

```text
http://localhost:5000/api/docs
```

---

# 🧪 Running Tests

## Backend Tests

```bash
cd backend

pytest
```

---

# 🐳 Docker Support

Run the application using Docker:

```bash
docker-compose up --build
```

This will start:

- Flask Backend
- PostgreSQL Database
- Supporting Services

---

# 👨‍💻 User Workflow

## 1. Register or Login

Create a new account or sign in using existing credentials.

## 2. Create or Join a Team

- Create a team and become Team Admin
- Join a team using an invite code

## 3. Create a Project

Set:

- Project Name
- Description
- Start Date
- End Date

## 4. Manage Tasks

- Create tasks
- Assign team members
- Update statuses
- Track priorities

## 5. Log Time

Record work hours and notes for completed tasks.

## 6. Review Analytics

Monitor project health and team productivity through dashboards.

---

# 🎯 Key Benefits

- Improved team collaboration
- Centralized project tracking
- Enhanced productivity monitoring
- Data-driven project analytics
- Built-in learning and reflection system
- Scalable architecture for future growth

---

# 📄 Documentation

Additional documentation is available in:

- `USER_GUIDE.md`
- `DEPLOYMENT.md`
- Swagger API Documentation

---

# 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Open a Pull Request
