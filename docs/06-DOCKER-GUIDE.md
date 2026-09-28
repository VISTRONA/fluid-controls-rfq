# 06 — Docker Guide

## Why Docker Is Required

Team members use different development environments.

Docker gives everyone approximately the same:

- Python version
- Node environment
- MySQL version
- dependency environment
- service networking

The project should not depend on one person's laptop configuration.

## Concepts

### Image

Template used to create a container.

### Container

Running instance of an image.

### Volume

Persistent data storage managed by Docker.

### Bind Mount

Maps source code from the host computer into a container.

### Docker Compose

Starts multiple project services together.

## Services

### frontend

Next.js development server.

Host:

    localhost:3000

### backend

FastAPI development server.

Host:

    localhost:8000

### db

MySQL.

Host:

    localhost:3306

Inside Docker, backend connects to:

    db:3306

NOT:

    localhost:3306

because `db` is the Compose service hostname.

## Environment

First setup:

    cp .env.example .env

Never commit `.env`.

## Start

    docker compose up --build

Detached:

    docker compose up -d --build

## View Containers

    docker compose ps

## Logs

All:

    docker compose logs -f

Backend:

    docker compose logs -f backend

Frontend:

    docker compose logs -f frontend

Database:

    docker compose logs -f db

## Stop

    docker compose down

## Rebuild One Service

    docker compose up -d --build backend

or:

    docker compose up -d --build frontend

## Backend Shell

    docker compose exec backend bash

## Run Tests

    docker compose exec backend pytest

## Apply Migrations

    docker compose exec backend alembic upgrade head

## MySQL Persistence

The database uses a named Docker volume.

Therefore:

    docker compose down

does not normally delete database contents.

WARNING:

    docker compose down -v

deletes project volumes.

Do not use `-v` unless intentionally resetting local development data.

## Hot Reload

Backend source:

    ./backend -> /app

Frontend source:

    ./frontend -> /app

Changes to source code should be visible to the development servers without rebuilding for normal source edits.

Rebuild when dependencies or Dockerfiles change.

## Windows

Recommended:

- Docker Desktop
- WSL2 enabled
- Git
- VS Code

Run project commands from WSL where practical.

## Linux

Use:

- Docker Engine
- Docker Compose plugin
- Git

## Important Rule

Do not solve environment problems by changing project dependencies only on your own computer.

Fix Docker/project configuration so the solution works for the entire team.
