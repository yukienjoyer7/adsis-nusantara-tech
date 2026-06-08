# Nusantara Tech — Development Environment in a Box

A fully containerized academic information system built with Docker Compose. Clone the repo, run one command, and have a full working environment.

## Stack

| Service | Technology |
|---------|-----------|
| Frontend | Vue 3 + Vite + Tailwind CSS |
| Backend | Python Flask + SQLAlchemy |
| Database | PostgreSQL 16 |
| Object Storage | MinIO |
| Reverse Proxy | Nginx |
| DB GUI | pgAdmin |

## Architecture

```
Internet
   ↓
Nginx (:80)
   ├── /                → frontend (Vue 3 + Vite)
   ├── /api/            → app (Flask REST API)
   └── /minio-console/  → minio (MinIO web console)

app (Flask)
   ├── db (PostgreSQL 16)
   └── minio (MinIO S3 API)

pgadmin → :5050 on host (direct)
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- Docker Compose v2 (`docker compose version`)

## Setup

**1. Clone the repo**
```bash
git clone <repo-url>
cd adsis-nusantara-tech
```

**2. Create your `.env` file**
```bash
cp .env.example .env
```

Then open `.env` and fill in your values:

```env
POSTGRES_PASSWORD=yourpassword
MINIO_ROOT_PASSWORD=yourminiopassword   # min 8 characters
SECRET_KEY=any-random-string
DATABASE_URL=postgresql://nusantara_user:yourpassword@db:5432/akademik
```

> Make sure `POSTGRES_PASSWORD` and the password in `DATABASE_URL` are identical.

**3. Start all services**
```bash
docker compose up -d
```

**4. Verify all 6 containers are running**
```bash
docker compose ps
```

## Access URLs

| Service | URL |
|---------|-----|
| Web App | http://localhost |
| MinIO Console | http://localhost/minio-console/ |
| MinIO S3 API | http://localhost:9000 |
| pgAdmin | http://localhost:5050 |

## Usage

1. Open http://localhost in your browser
2. Register an account with your name, NIM, email, and password
3. Log in with your NIM and password
4. Upload and manage your files from the dashboard

## API Endpoints

All endpoints are available at `http://localhost/api/`.

**Auth**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Create account (name, nim, email, password) |
| POST | `/api/login` | Login with NIM + password |
| POST | `/api/logout` | End session |
| GET | `/api/me` | Get current user profile |

**Files** (login required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/files` | Upload a file (multipart form-data, key: `file`) |
| GET | `/api/files` | List your uploaded files |
| GET | `/api/files/<filename>` | Download a file (redirects to presigned URL) |
| DELETE | `/api/files/<filename>` | Delete a file |

## Teardown

```bash
docker compose down        # stop containers, keep data
docker compose down -v     # stop containers, delete all data
```

## Screenshots

### Login & Register
<img width="1792" height="1074" alt="Screenshot 2026-06-08 at 12 08 20" src="https://github.com/user-attachments/assets/1f9433a0-3b8b-43b3-9a76-f39f1baa5412" />
<img width="1792" height="1074" alt="Screenshot 2026-06-08 at 12 08 28" src="https://github.com/user-attachments/assets/5d203dd5-4dce-48fc-8027-ef85950b39b2" />


### Dashboard
<img width="1792" height="1074" alt="Screenshot 2026-06-08 at 12 08 47" src="https://github.com/user-attachments/assets/cea62fab-f202-4194-b03b-1e292a3565a6" />
<img width="1792" height="1074" alt="Screenshot 2026-06-08 at 13 03 01" src="https://github.com/user-attachments/assets/7f0d5c78-f5c6-4bbc-8ce1-d0ad875dbec9" />
<img width="1792" height="1074" alt="Screenshot 2026-06-08 at 13 05 23" src="https://github.com/user-attachments/assets/ec1eeb32-49b8-4245-884e-df45273a3239" />
<img width="1792" height="1074" alt="Screenshot 2026-06-08 at 13 02 53" src="https://github.com/user-attachments/assets/83cade7b-e2a7-4b37-b461-d2ea0c86afbc" />

### MinIO Bucket
![MinIO](screenshots/minio.png)

### pgAdmin
![pgAdmin](screenshots/pgadmin.png)
