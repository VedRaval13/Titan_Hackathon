# TITANS — AI-Powered Workforce Recommendation & Task Management

<p align="center">
  <img src="frontend/public/logo.png" alt="TITANS Logo" width="200" />
</p>

<p align="center">
  <strong>Intelligent task assignment powered by AI with seamless Jira integration</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/Jira-Cloud-0052CC?logo=jira" />
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4?logo=google" />
  <img src="https://img.shields.io/badge/Tests-17%20Passing-brightgreen" />
</p>

---

## About

**TITANS** is an AI-powered platform that recommends the best employee for every task by analyzing skills, experience, workload, and availability. It features **bidirectional Jira sync** — changes made in TITANS appear in Jira and vice versa, eliminating double data entry.

Built for **GLS Nexus Hackathon 2026** by **Team TITANS** (Ved Raval & Het Patel).

---

## Features

- **AI Recommendations** — Gemini AI analyzes tasks and recommends the top 3 employees with explanations
- **Bidirectional Jira Sync** — Tasks, status, priority, and assignees sync both ways automatically
- **Employee Management** — Track skills, availability, workload, and assignment history
- **Settings Panel** — Connect any Jira server with one click; auto-imports team members and tasks
- **Fresh Start** — Switching to a new Jira server wipes old data and imports everything fresh
- **Auto-Sync** — Changes in Jira appear in TITANS within 30 seconds
- **Manager Controls** — Approve AI recommendations or override with your own choice

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Tailwind CSS, React Query, React Router, Lucide Icons |
| Backend | Python 3.13, FastAPI, SQLAlchemy (async), Pydantic v2 |
| Database | SQLite with aiosqlite |
| AI | Google Gemini API |
| Integration | Jira Cloud REST API v3 |
| Testing | Pytest (17 automated tests) |

---

## Project Structure

```
titans/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings & environment config
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── task.py
│   │   │   ├── employee.py
│   │   │   ├── recommendation.py
│   │   │   ├── assignment.py
│   │   │   └── run_log.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── task.py
│   │   │   ├── employee.py
│   │   │   ├── recommendation.py
│   │   │   └── assignment.py
│   │   ├── routers/             # API endpoints
│   │   │   ├── tasks.py         # CRUD + Jira sync
│   │   │   ├── employees.py     # CRUD + Jira user sync
│   │   │   ├── recommendations.py
│   │   │   └── settings.py      # Jira configuration
│   │   ├── services/            # Business logic
│   │   │   ├── jira_service.py  # Jira API client
│   │   │   ├── ai_service.py    # Gemini AI integration
│   │   │   └── recommendation_engine.py
│   │   └── core/
│   │       └── middleware.py    # CORS & request logging
│   ├── tests/                   # 17 automated tests
│   ├── seed.py                  # Database seeder
│   ├── requirements.txt
│   └── .env                     # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api/client.js        # Axios API client
│   │   ├── hooks/               # React Query hooks
│   │   ├── pages/               # Dashboard, Tasks, Employees, etc.
│   │   └── components/          # Navbar, badges, charts
│   ├── public/logo.png
│   └── package.json
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/titans.git
cd titans
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key
FRONTEND_URL=http://localhost:5173
```

Seed the database and start the server:

```bash
python seed.py
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### 4. Connect Jira (Optional)

1. Go to **Settings ⚙️** in the navbar
2. Enter your Jira URL, Email, API Token, and Project Key
3. Click **Save & Connect**
4. Team members and tasks are auto-imported!

> Generate an API token at: https://id.atlassian.com/manage-profile/security/api-tokens

---

## How It Works

### AI Recommendations

1. Select a task → Click **Generate Recommendations**
2. Gemini AI analyzes the task and ranks employees
3. Top 3 candidates shown with match scores and explanations
4. Manager **approves** the best pick or **overrides** with their choice
5. Employee is assigned → Jira assignee updated automatically

### Jira Bidirectional Sync

| TITANS → Jira | Jira → TITANS |
|----------------|----------------|
| Create task → Creates Jira issue | New Jira issue → Appears in TITANS |
| Edit title/priority/status → Updates in Jira | Edit in Jira → Updates in TITANS |
| Assign employee → Sets Jira assignee | Assign in Jira → Sets TITANS employee |

Auto-syncs every 30 seconds. Manual sync available via the **Sync Jira** button.

### Fresh Start on New Jira

When you connect a **new Jira server** (different URL or project key):
- All old data is wiped (tasks, employees, recommendations, assignments)
- Team members are auto-imported from the new Jira
- Tasks are auto-imported with assignee matching
- Dashboard shows only the new Jira data

---

## API Endpoints

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Create task (optional Jira push) |
| PUT | `/api/tasks/{id}` | Update task (syncs to Jira) |
| POST | `/api/tasks/jira/sync` | Pull tasks from Jira |
| GET | `/api/tasks/jira/status` | Check Jira connection |

### Employees
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees` | List all employees |
| POST | `/api/employees` | Create employee |
| PUT | `/api/employees/{id}` | Update employee |
| POST | `/api/employees/jira/sync` | Pull team members from Jira |

### Recommendations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recommendations/generate/{task_id}` | Generate AI recommendations |
| GET | `/api/recommendations/{task_id}` | Get recommendations for a task |
| POST | `/api/recommendations/{id}/approve` | Approve (assigns + syncs Jira) |
| POST | `/api/recommendations/{id}/override` | Override with different employee |

### Settings
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settings/jira` | Get Jira config (token masked) |
| POST | `/api/settings/jira` | Save Jira config (fresh start if changed) |
| POST | `/api/settings/jira/test` | Test Jira connection |

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

```
17 passed ✅
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `JIRA_BASE_URL` | Jira Cloud URL (e.g. https://team.atlassian.net) | No (set in Settings) |
| `JIRA_EMAIL` | Jira account email | No (set in Settings) |
| `JIRA_API_TOKEN` | Jira API token | No (set in Settings) |
| `JIRA_PROJECT_KEY` | Jira project key (e.g. MP) | No (set in Settings) |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes |
| `FRONTEND_URL` | Frontend URL for CORS | Yes |

---

## Team

**Team TITANS** — GLS Nexus Hackathon 2026

- **Ved Raval**
- **Het Patel**

---

## License

This project was built for GLS Nexus Hackathon 2026.
