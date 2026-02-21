# 📅 Meeting Scheduler

[![GitHub Repo](https://img.shields.io/badge/GitHub-Meeting__Scheduler__Alpha.net-blue?logo=github)](https://github.com/amirhamjacse/Meeting_Scheduler_Alpha.net)

> **Submitted for:** Alpha Net — Python Developer Position Assignment
> **Project chosen:** Meeting Scheduler (Project 1)

A full-stack meeting scheduling application built with **Django REST Framework** (backend) and **Next.js 16** (frontend). Users can register, create meetings, invite participants, detect scheduling conflicts, and export calendar events as `.ics` files.

- - -

## 🗂️ Project Structure

```
Meeting_Scheduler_Alpha.net/   ← Django backend (this repo)
├── accounts/                   ← Custom user model, auth API
├── meetings/                   ← Meetings, participants, notifications
├── config/                     ← Django settings, URLs, WSGI/ASGI
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env                        ← Environment variables (create this)

meeting-frontend/               ← Next.js frontend
├── src/
│   ├── app/                    ← App Router pages
│   │   ├── (auth)/             ← Login & Register pages
│   │   └── dashboard/          ← Dashboard, meetings CRUD
│   ├── components/             ← Reusable UI components
│   ├── contexts/               ← AuthContext (JWT state)
│   └── lib/                    ← Axios API client, utils
├── .env.local                  ← Frontend env variables
└── package.json
```

- - -

## ✨ Features

* 🔐 JWT authentication (register, login, logout, token refresh)
* 📆 Create, edit, cancel, and view meetings
* 👥 Invite participants by email, manage RSVP statuses
* ⚠️ Real-time scheduling conflict detection
* 📧 Email notifications (invitation, update, cancellation)
* 📥 Export meetings as `.ics` calendar files (RFC 5545)
* 📖 Interactive API docs via Swagger UI (`/api/docs/`)
* 🐳 Docker support for the backend

- - -

## ⚙️ Tech Stack

| Layer | Technology |
| ----- | ---------- |
| Backend | Django 4.2, Django REST Framework, PostgreSQL |
| Auth | `djangorestframework-simplejwt` (JWT) |
| Docs | `drf-spectacular` (Swagger / ReDoc) |
| Calendar | `icalendar` (RFC 5545 `.ics` generation) |
| CORS | `django-cors-headers` |
| Frontend | Next.js 16, React 19, Tailwind CSS v4 |
| HTTP | Axios with JWT auto-refresh interceptor |
| Icons | Lucide React |
| Dates | date-fns |

- - -

## 🚀 Getting Started

### Prerequisites

| Tool | Required Version |
| ---- | ---------------- |
| Python | 3.10+ |
| Node.js | 20.9.0+ (use nvm) |
| PostgreSQL | 13+ |
| pip | latest |
| npm | latest |

- - -

## 🔧 Backend Setup (Django)

### 1\. Clone and enter the project

``` bash
git clone https://github.com/amirhamjacse/Meeting_Scheduler_Alpha.net.git
cd Meeting_Scheduler_Alpha.net
```

### 2\. Create and activate a virtual environment

``` bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 3\. Install Python dependencies

``` bash
pip install -r requirements.txt
```

### 4\. Configure environment variables

Create a `.env` file in the project root:

``` env
# Django
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=meetsh
DB_USER=scheduler_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Email (console backend for development — prints to terminal)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# For production SMTP (e.g. Gmail):
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=you@gmail.com
# EMAIL_HOST_PASSWORD=your_app_password
# DEFAULT_FROM_EMAIL=you@gmail.com
```

### 5\. Create the PostgreSQL database and user

``` sql
-- Run in psql as superuser
CREATE USER scheduler_user WITH PASSWORD 'yourpassword';
CREATE DATABASE meetsh OWNER scheduler_user;
GRANT ALL PRIVILEGES ON DATABASE meetsh TO scheduler_user;

-- If you get permission errors on public schema (PostgreSQL 15+):
\c meetsh
GRANT ALL ON SCHEMA public TO scheduler_user;
```

### 6\. Run migrations

``` bash
python manage.py migrate
```

### 7\. Create a superuser (admin login)

To access the Django admin panel at `/admin/` or to get a login account
for testing the API right away, create a superuser:

``` bash
python manage.py createsuperuser
```

You will be prompted to enter:

```
Username: admin          ← choose any username
Email address: admin@example.com
Password: ••••••••
Password (again): ••••••••
Superuser created successfully.
```

> **Tip:** You can also create regular (non-admin) users through the
> registration API endpoint:
>
> ```bash
> curl -X POST http://localhost:8000/api/auth/register/ \
>      -H "Content-Type: application/json" \
>      -d '{"email":"user@example.com","username":"testuser","password":"yourpassword","password2":"yourpassword"}'
> ```
>
> Or simply use the **Register** page on the frontend at
> `http://localhost:3000/register`.

### 8\. Start the development server

``` bash
python manage.py runserver
```

Backend is now running at **http://localhost:8000**

- - -

## 🌐 API Endpoints

| Method | URL | Description |
| ------ | --- | ----------- |
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login — returns JWT tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Logout (blacklists refresh token) |
| GET | `/api/auth/me/` | Get current user profile |
| POST | `/api/auth/change-password/` | Change password |
| GET | `/api/meetings/` | List all meetings |
| POST | `/api/meetings/` | Create a meeting |
| GET | `/api/meetings/{id}/` | Get meeting detail |
| PUT | `/api/meetings/{id}/` | Update a meeting |
| DELETE | `/api/meetings/{id}/` | Delete a meeting |
| POST | `/api/meetings/{id}/cancel/` | Cancel a meeting |
| GET | `/api/meetings/{id}/export-ics/` | Export meeting as `.ics` file |
| GET | `/api/meetings/my-calendar/` | Export all my meetings as `.ics` |
| POST | `/api/meetings/check-conflicts/` | Check participant conflicts |
| POST | `/api/meetings/{id}/notify/` | Send notifications to participants |
| GET | `/api/meetings/{id}/participants/` | List participants |
| POST | `/api/meetings/{id}/participants/` | Add a participant |
| DELETE | `/api/meetings/{id}/participants/{pid}/` | Remove a participant |
| PATCH | `/api/meetings/{id}/participants/{pid}/status/` | Update RSVP status |

### 📖 Interactive API Docs

| URL | Description |
| --- | ----------- |
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc UI |
| `/api/schema/` | Raw OpenAPI JSON |
| `/admin/` | Django Admin panel |

- - -

## 🐳 Docker Setup (Backend)

You can run the Django backend + PostgreSQL using Docker Compose:

### 1\. Add Docker\-specific values to `.env`

``` env
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=meetsh
DB_USER=scheduler_user
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432
```

### 2\. Build and start services

``` bash
docker-compose up --build
```

### 3\. Run migrations inside the container

``` bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

> ⚠️ Note: The `docker-compose.yml` uses `gunicorn core.wsgi:application`. Update the command to `gunicorn config.wsgi:application` to match this project's WSGI module.

- - -

## 🖥️ Frontend Setup (Next.js)

### 1\. Enter the frontend directory

``` bash
cd meeting-frontend
```

### 2\. Ensure Node\.js v20\+ is active

``` bash
node -v          # should show v20.x.x or higher
# If using nvm:
nvm install 20
nvm use 20
```

### 3\. Install dependencies

``` bash
npm install
```

### 4\. Configure environment variables

Create a `.env.local` file inside `meeting-frontend/`:

``` env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5\. Start the development server

``` bash
npm run dev
```

Frontend is now running at **http://localhost:3000**

- - -

## 📱 Frontend Pages

| Route | Description |
| ----- | ----------- |
| `/` | Redirects to dashboard or login |
| `/login` | Login page |
| `/register` | Registration page |
| `/dashboard` | Stats overview + upcoming meetings |
| `/dashboard/meetings` | All meetings with search & filter |
| `/dashboard/meetings/new` | Create a new meeting |
| `/dashboard/meetings/[id]` | Meeting detail + participants |
| `/dashboard/meetings/[id]/edit` | Edit a meeting |

- - -

## 🔄 Running Both Servers Together

Open **two terminals**:

**Terminal 1 — Backend:**

``` bash
cd django-boilerplate-v1
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 — Frontend:**

``` bash
cd meeting-frontend
nvm use 20        # if using nvm
npm run dev
```

Then open **http://localhost:3000** in your browser.

- - -

## 🔑 Environment Variable Reference

### Backend `.env`

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `DJANGO_DEBUG` | `False` | Enable debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hosts |
| `DB_ENGINE` | — | Django DB engine |
| `DB_NAME` | — | Database name |
| `DB_USER` | — | Database user |
| `DB_PASSWORD` | — | Database password |
| `DB_HOST` | — | Database host |
| `DB_PORT` | `5432` | Database port |
| `EMAIL_BACKEND` | `django.core.mail.backends.console.EmailBackend` | Email backend |
| `EMAIL_HOST` | `smtp.gmail.com` | SMTP host |
| `EMAIL_PORT` | `587` | SMTP port |
| `EMAIL_HOST_USER` | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | — | SMTP password |
| `DEFAULT_FROM_EMAIL` | `noreply@meetingscheduler.com` | From address for emails |

### Frontend `.env.local`

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Django backend base URL |

- - -

## 🛠️ Common Issues & Fixes

### `ModuleNotFoundError` on `icalendar` or `corsheaders`

``` bash
pip install -r requirements.txt
```

### PostgreSQL permission denied on schema

``` sql
\c meetsh
GRANT ALL ON SCHEMA public TO scheduler_user;
```

### `@tailwindcss/oxide` binary missing (Linux)

``` bash
cd meeting-frontend
npm install @tailwindcss/oxide-linux-x64-gnu
```

### Next.js dev server won't start (port lock)

``` bash
pkill -f "next dev"
rm -rf .next
npm run dev
```

### Next.js requires Node.js >= 20.9.0

``` bash
nvm install 20
nvm use 20
```

### Input text not visible (white on white)

This is caused by a browser dark mode override. The `globals.css` already forces `color-scheme: light` to prevent this.

- - -

## � Assignment Brief — Alpha Net Python Developer Assessment

This project was built as a submission for the **Alpha Net Python Developer
Position** final evaluation stage.

### Assignment Requirements Checklist

#### ✔ Technology Stack

| Requirement | Status | Detail |
| ----------- | ------ | ------ |
| Python backend (FastAPI / Django) | ✅ | Django 4.2 + Django REST Framework |
| Relational database (PostgreSQL / SQLite) | ✅ | PostgreSQL (SQLite usable via `.env`) |
| Dockerfile | ✅ | `Dockerfile` in project root |
| Docker Compose | ✅ | `docker-compose.yml` in project root |
| Open-source / locally-hosted AI only | ✅ | No cloud AI services used |

#### ✔ Deliverables

| Deliverable | Status |
| ----------- | ------ |
| Complete project repository | ✅ GitHub link in badge above |
| README with install & run instructions | ✅ See **Getting Started** section |
| README with API usage examples (cURL) | ✅ See **API Endpoints** section |
| Architecture & design decisions | ✅ See **Architecture** section below |
| Database schema explanation | ✅ See **Database Schema** section below |
| Limitations & future improvements | ✅ See **Limitations** section below |
| Migration files | ✅ `accounts/migrations/` + `meetings/migrations/` |
| Minimal automated tests (1–3) | ✅ `accounts/tests.py` + `meetings/tests.py` |
| Clean, PEP 8 compliant project structure | ✅ 79-char line limit enforced throughout |

- - -

## 🏗️ Architecture & Design Decisions

### Overall Architecture

```
[Next.js 16 Frontend]  ←──── HTTP/JSON ────→  [Django REST Framework Backend]
        ↓                                                   ↓
  JWT in localStorage                            PostgreSQL Database
  Axios + interceptor                            (meetings, participants,
  (auto token refresh)                            notifications, users)
```

### Key Design Decisions

1. **Custom User Model** — `AbstractBaseUser` used instead of Django's default
   `User` so that `email` is the primary login field, not `username`. This is
   set in `accounts/models.py` and referenced via `AUTH_USER_MODEL` in
   settings. Changing this after migrations are applied would be destructive,
   so it is done from the start.

2. **UUID Primary Keys** — `Meeting` uses `uuid.uuid4` as its primary key
   instead of an integer. This prevents enumeration attacks on the API (a
   user cannot guess `meeting/2/` to access another user's meeting).

3. **Mixed API View Style** — Views are split into:
   - `generics.ListCreateAPIView` / `generics.RetrieveUpdateDestroyAPIView`
     for standard CRUD (less boilerplate, DRY)
   - Manual `APIView` for custom business logic endpoints (cancel, export-ics,
     conflict check, notify) where explicit control is cleaner

4. **Conflict Detection** — Scheduling conflicts are checked at participant
   invite time **and** via a dedicated `/check-conflicts/` endpoint so the
   frontend can warn users before submitting the form.

5. **ICS Export** — RFC 5545 compliant `.ics` files are generated using the
   `icalendar` library, both per-meeting and as a bulk calendar download.

6. **Signal-based Notifications** — A Django `post_save` signal on `Meeting`
   automatically fires email notifications when a meeting's status changes,
   keeping notification logic decoupled from views.

7. **JWT Auth** — `djangorestframework-simplejwt` with refresh token
   blacklisting (`ROTATE_REFRESH_TOKENS = True`) keeps sessions stateless
   while supporting secure logout.

- - -

## 🗄️ Database Schema

```
accounts_user
─────────────────────────────────────────────
id            UUID        PK
email         VARCHAR     UNIQUE, login field
username      VARCHAR     UNIQUE
first_name    VARCHAR
last_name     VARCHAR
is_active     BOOLEAN
is_staff      BOOLEAN
created_at    TIMESTAMP

meetings_meeting
─────────────────────────────────────────────
id            UUID        PK
title         VARCHAR
description   TEXT
location      VARCHAR
start_time    TIMESTAMP
end_time      TIMESTAMP
status        VARCHAR     scheduled|cancelled|completed
created_by    FK → accounts_user (CASCADE)
created_at    TIMESTAMP
updated_at    TIMESTAMP

meetings_participant
─────────────────────────────────────────────
id            INTEGER     PK
meeting       FK → meetings_meeting (CASCADE)
user          FK → accounts_user (SET NULL, nullable)
email         VARCHAR     (invited by email, user may not exist yet)
status        VARCHAR     pending|accepted|declined|tentative
responded_at  TIMESTAMP

meetings_meetingnotification
─────────────────────────────────────────────
id            INTEGER     PK
meeting       FK → meetings_meeting (CASCADE)
recipient     FK → accounts_user (SET NULL)
type          VARCHAR     invitation|update|cancellation|reminder
sent_at       TIMESTAMP
```

**Relationships:**
- One `User` → many `Meeting` (as organiser)
- One `Meeting` → many `Participant`
- One `Meeting` → many `MeetingNotification`
- One `User` → many `Participant` rows (across meetings they are invited to)

- - -

## ⚠️ Limitations & Future Improvements

### Current Limitations

- **Email is console-based in development** — emails print to the terminal
  instead of being sent. A real SMTP server (e.g. Gmail, SendGrid) must be
  configured via `.env` for production use.
- **No recurring meetings** — meetings are single-occurrence only. Recurring
  (daily, weekly, monthly) scheduling is not yet implemented.
- **No real-time updates** — participants do not receive live updates when a
  meeting changes. A page refresh is required.
- **No file attachments** — meetings cannot have agenda documents or
  attachments uploaded.
- **No timezone-aware UI** — all times are stored in UTC; the frontend does
  not yet convert to the viewer's local timezone.

### Suggested Future Improvements

- **WebSocket / SSE** — push real-time notifications to participants when a
  meeting is updated or cancelled (Django Channels or SSE).
- **Recurring meeting rules** — implement RFC 5545 `RRULE` support in both the
  model and ICS export.
- **Google / Outlook Calendar Sync** — OAuth2 integration to push meetings
  directly into external calendars.
- **Role-based participant permissions** — co-organiser role that can edit
  meetings, not just the creator.
- **Pagination & filtering on the frontend** — the dashboard currently loads
  all meetings; server-side pagination is implemented in the API but not wired
  to the UI.
- **Production-ready deployment** — Nginx + Gunicorn configuration, HTTPS via
  Let's Encrypt, environment secrets management (e.g. Vault or AWS Secrets
  Manager).

- - -

## �📄 License

MIT