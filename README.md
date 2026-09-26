# JEV DecisionOps

A structured invoice decision engine powered by TypeSafe JEV.

## Overview

JEV DecisionOps evaluates invoice and vendor data with TypeSafe JEV, then applies a small deterministic policy to return `AUTO_APPROVE`, `HUMAN_REVIEW`, or `REJECT`.

## How It Works

Invoice Data → FastAPI → TypeSafe JEV → Risk / Routing / Review Signals → Deterministic Policy → Approve / Review / Reject

## Architecture

```
Invoice Form
  → FastAPI
  → TypeSafe JEV
  → Structured Decision Signals
  → Simple Policy Rules
  → Result
  → Recent Decisions
```

## Features

- Invoice evaluation form
- TypeSafe JEV risk, route, review, reliability, and priority signals
- Deterministic approve / review / reject policy
- Fail-safe human review when JEV is unavailable
- Session metrics and recent decisions (in-memory)

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Backend: Python, FastAPI, Pydantic, TypeSafe Python SDK

## Project Structure

```
Jev DecisionOps/
├── backend/
│   ├── main.py
│   ├── jev_service.py
│   ├── decision_policy.py
│   ├── models.py
│   └── requirements.txt
├── frontend/
├── .env.example
└── README.md
```

## Setup

Copy `.env.example` to `.env` and add your TypeSafe API key.

## Environment Variables

```
TYPESAFE_API_KEY=
JEV_MODEL=jev-latest
```

Optional frontend override:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running Backend

```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Running Frontend

```
cd frontend
npm install
npm run dev
```

Open http://localhost:3000. The API runs at http://localhost:8000.

## Safety / Fail-Safe Behavior

If TypeSafe JEV times out, errors, cannot authenticate, or returns malformed data, the policy returns `HUMAN_REVIEW` with `fallback_used=true`. The system never auto-approves because the provider failed.
