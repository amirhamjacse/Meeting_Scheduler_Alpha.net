# 📅 Meeting Scheduler

[![GitHub Repo](https://img.shields.io/badge/GitHub-Meeting__Scheduler__Alpha.net-blue?logo=github)](https://github.com/amirhamjacse/Meeting_Scheduler_Alpha.net)

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

## 📄 License

MIT