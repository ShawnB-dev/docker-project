# Stage 1: Build dependencies
FROM python:3.14-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Final Runtime
FROM python:3.14-slim

# Setup non-privileged user for security
RUN useradd -m appuser
WORKDIR /home/appuser/app

# Copy only the installed dependencies from the builder stage
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 5000

# Default command (overridden by docker-compose for the honeypot)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "app:app"]
