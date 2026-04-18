# Stage 1: Build dependencies
FROM python:3.14-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: Final Runtime
FROM python:3.14-slim

# Create a non-privileged user and setup directories
RUN useradd -m appuser
WORKDIR /home/appuser/app

# Copy only the installed dependencies from the builder stage
COPY --from=builder /install /usr/local
COPY --chown=appuser:appuser app.py .

USER appuser

EXPOSE 5000

# Use Gunicorn with access logging enabled for better observability
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "app:app"]
