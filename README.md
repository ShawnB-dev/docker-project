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
- **Honeypot:** Decoy service that traps and logs malicious activities.

## Honeypot Features
- **Decoy Admin Portal:** A realistic, dark-themed login interface designed to bait automated scanners and brute-force bots.
- **Pattern-Based Trapping:** Nginx identifies and redirects high-risk paths (`/admin`, `.env`, `phpmyadmin`, etc.) to the honeypot.
- **Credential Harvesting:** Captures attempted usernames and passwords from brute-force attempts.
- **Email Decoy:** A "Forgot Password" workflow that harvests email addresses and validates inputs via RFC 5322 compliant regex.
- **Sophisticated Logging:** Distinguishes between scanning (GET), brute-force (POST), and malformed inputs to provide clear threat intelligence.
- **CLI Intelligence:** A dedicated utility (`cli.py`) to export captured logs into structured Excel or CSV reports.

## How it Works
1. **Interception:** The Nginx reverse proxy monitors incoming traffic. It uses regular expression matching to detect requests aimed at common vulnerability targets (e.g., WordPress login pages or exposed Git directories).
2. **Redirection:** When a signature is matched, Nginx silently proxies the request to the `honeypot` container. The attacker is never aware they have left the main application network.
3. **Engagement:** The honeypot serves a convincing UI and provides realistic feedback. For example, it returns a `401 Unauthorized` status code on login failure to encourage bots to continue their brute-force attempts, allowing for more data collection.
4. **Persistence & Analysis:** All alerts are written to a shared volume (`app_logs`). This data can be analyzed in real-time via `docker-compose logs` or exported using the CLI tool for offline forensics.

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