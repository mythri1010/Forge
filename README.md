# Forge
A team task tracker that visualizes workflows and automatically computes project‑management metrics like lead time, cycle time, throughput, and workload per developer.

# 📂 Project Structure
forge/
/
├── backend/    Flask API server
├── frontend/   Next.js dashboard
├── .gitignore
└── README.md

# ⚙️ Prerequisites
Before running the project, ensure you have the following installed:
- Python 3.11+
- Node.js 18+
- PostgreSQL (running locally)

# 🚀 Getting Started
Backend Setup
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Apply database migrations
flask db upgrade

# Start the backend server
python run.py

Backend API will be available at:
http://localhost:5000
Frontend Setup
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.local.example .env.local

# Start development server
npm run dev

Frontend application will be available at:
http://localhost:3000
✨ Features
👥 Team Management

Users can:

Create a new team and become the Team Admin.
Generate and share invite codes.
Join existing teams using invite codes.
Collaborate with team members across projects.

# 📁 Project Management
Create and manage projects by specifying:
- Project name
- Description
- Start date
- End date (optional)

Projects provide a centralized workspace for team collaboration and progress tracking.

# ✅ Task Management (Kanban Board)

Each project includes a Kanban board where tasks can be created and managed.

Task Statuses
- TODO
- IN_PROGRESS
- IN_REVIEW
- BLOCKED
- DONE
Task Priorities
- LOW
- MEDIUM
- HIGH
- CRITICAL

Additional features:

- Assign tasks to team members
- Set due dates
- Edit task details
- Track work progress
- Log time spent on tasks
