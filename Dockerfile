# ─────────────────────────────────────────────────────────────────────────────
# DeciSphere AI – Dockerfile
# FastAPI backend for Hugging Face Spaces / Docker deployment
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.10-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy full project
COPY . .

# Expose FastAPI port
EXPOSE 7860

# Python settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check for FastAPI
HEALTHCHECK CMD curl --fail http://localhost:7860/ || exit 1

# Start FastAPI app
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]