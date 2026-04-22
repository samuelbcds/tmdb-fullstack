<p align="center">
	<img src="tmdb-front/tmdb-front/src/assets/icons/a-star-that-can-be-used-for-favorites-and-recommendations-svgrepo-com.svg" alt="TMDB Fullstack icon" width="72" />
</p>

# TMDB Fullstack

A full-stack movie app built with **Flask** on the backend and **React + Vite** on the frontend.
It integrates with the TMDB API for search and stores user ratings + rated films data in a Postgres database.

## Features

- JWT auth using HTTP-only cookies

- Browse popular movies from TMDB

- Search and filter by title, year, and genre

- Save and track personal ratings on each movie

- Filter rated movies to find them easily

- Docker Compose setup for one-command local run

## Tech Stack

- Backend: Flask 3, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, Poetry

- Frontend: React 19, TypeScript, Vite, React Router, Axios

- Database: PostgreSQL

- Runtime: Docker

## Architecture

```text
tmdb/
|- docker-compose.yml
|- .env.example
|- tmdb-app/                 # Flask API
|  |- run.py
|  |- src/
|     |- routes/routes.py
|     |- controllers/
|     |- models/
|- tmdb-front/               # React app
   |- src/
      |- pages/
      |- services/
      |- routes/
      |- context/
      |- hooks/
      |- routes/
```

## Quick Start with Docker

1. At root directory, copy environment variables:

```bash
cp .env.example .env
```

2. Set your TMDB key in `.env`:

```env
VITE_TMDB_API_KEY=your_tmdb_api_key
```

3. Build and run:

```bash
docker compose up --build
```

4. Open:

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:5000/api`
- Health check: `http://localhost:5000/api/health`

> Docker is the recommended path.

## Local Development

### 1) Start PostgreSQL

Use your local PostgreSQL instance and configure the local DB url at the .env, located on tmdb-app folder, filling SQLALCHEMY_DATABASE_URI with your db credentials

```env
SQLALCHEMY_DATABASE_URI=your_db_uri
```

### 2) Run backend

```bash
cd tmdb-app
poetry install
poetry run python run.py
```

Backend runs on `http://localhost:5000`.

### 3) Run frontend

```bash
cd tmdb-front/tmdb-front
npm ci
npm run dev
```

Frontend dev server runs on `http://localhost:5173`.

## API Summary

Base URL: `/api`

### Auth

- `POST /login`
- `POST /refresh`
- `DELETE /logout`
- `DELETE /logout2`

### Users

- `POST /users` (register)
- `GET /users/me` (current user)

### Movies

- `POST /movies` (save/update rated movie)
- `GET /movies` (paginated list with filters: `search`, `year`, `genre`, `min_rating`, `page`, `per_page`)
- `GET /movies/:movie_id`
- `PUT /movies/:movie_id/rate`

## Frontend Routes

- `/login`
- `/register`
- `/` (protected; TMDB discovery/search)
- `/rated-movies` (protected; locally rated movies)
- `/movies/:movieId` (protected; details + rating)

## Useful Commands

```bash
#Clean reset
docker compose down -v
```

