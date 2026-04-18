# Docker and Honeypot Implementation Project

A production-ready Dockerized Python application demonstrating multi-container orchestration, reverse proxy integration, and persistent storage.

## Tech Stack
- **Backend:** Python 3.14 (Flask + Gunicorn)
- **Proxy:** Nginx (Reverse Proxy)
- **Data Store:** Redis (with Append-Only persistence)
- **CI/CD:** GitHub Actions

## Architecture
- **Nginx:** Listens on port 80 and proxies traffic to the Flask app.
- **Web (Flask):** Handles requests and communicates with Redis via an internal Docker network.
- **Redis:** Stores hit counts in a named volume to ensure data survives container restarts.

## Features
- **Multi-stage Builds:** Optimized Docker image size using Python 3.14-slim.
- **Security:** Runs as a non-privileged `appuser`.
- **Health Checks:** Ensures the web service only starts once Redis is ready.
- **Persistence:** Redis data is mapped to a local volume.

## Getting Started

### Prerequisites
- Docker Desktop installed
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/docker-project.git
   cd docker-project
   ```
2. Launch the stack:
   ```bash
   docker-compose up -d --build
   ```
3. Access the application:
   Open http://localhost in your browser.

## Running Tests
Check container health: `docker-compose ps`