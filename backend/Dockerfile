FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application as a package to preserve import paths
COPY backend/ backend/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import os, httpx; port = os.getenv('PORT', '8000'); httpx.get(f'http://localhost:{port}/api/v1/health')"

# Run the application
CMD ["python", "-m", "backend.main"]
