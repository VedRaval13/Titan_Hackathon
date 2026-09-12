# 🏛️ TITANS — AI-Powered Workforce Recommendation & Optimization

**Team TITANS** | Ved Raval & Het Patel | GLS Nexus Hackathon 2026

## Overview
TITANS is an AI-driven workforce recommendation and optimization platform. It analyzes tasks from Jira using Google Gemini and intelligently matches them to the most suitable employees based on skills, experience, and current workload. It ensures optimal task distribution across the workforce.

## Architecture
- **Task Processor**: Ingests tasks from Jira webhooks or manual syncing.
- **AI Analysis**: Uses Gemini 1.5 Flash to extract required skills, difficulty, and categorization from unstructured task descriptions.
- **Recommendation Engine**: Scores employees based on skill match, experience, workload, and availability to suggest the best candidates.
- **Manager Review**: Allows human managers to review, approve, or override AI recommendations.
- **Optimization Engine**: Uses OR-Tools to globally balance workload across the entire organization, preventing employee burnout.

## Tech Stack
- Backend: Python 3.11 + FastAPI
- Database: PostgreSQL + SQLAlchemy
- AI: Google Gemini 1.5 Flash
- Optimization: OR-Tools (CP-SAT Solver)
- Frontend: React + Tailwind CSS
- Auth: JWT

## Quick Start

### Prerequisites
- Docker & Docker Compose
- OR: Python 3.11+, Node.js 20+, PostgreSQL 16

### Using Docker (Recommended)
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys
docker-compose up --build
```
Frontend: http://localhost
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints
- `POST /api/auth/login`: Authenticate and get JWT token.
- `GET /api/tasks`: List all tasks.
- `POST /api/tasks/sync`: Sync tasks from Jira.
- `GET /api/employees`: List all employees.
- `GET /api/recommendations/{task_id}`: Get top recommended employees for a task.
- `POST /api/optimize`: Run the global optimization engine.
- `POST /api/assignments`: Finalize and save task assignments.

## Environment Variables
| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JIRA_BASE_URL` | Your Jira instance URL |
| `JIRA_EMAIL` | Jira account email |
| `JIRA_API_TOKEN` | Jira API token for authentication |
| `GEMINI_API_KEY` | Google Gemini API key |
| `JWT_SECRET_KEY` | Secret key for JWT signing |
| `FRONTEND_URL` | URL of the frontend application |

## How It Works
1. Tasks come in from Jira (webhook/manual)
2. Gemini AI analyzes task requirements
3. Recommendation engine scores all employees
4. Manager reviews and approves/overrides
5. OR-Tools optimizer balances workload globally

## Business Rules
- AI analyzes, never assigns
- Recommendations suggest, managers decide
- Every recommendation has a human-readable reason
- Workload capped at 8.0 per employee

## License
MIT
