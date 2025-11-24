# force-rebuild-final

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy NEW deps file (cache invalidation)
COPY requirements1.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install all dependencies fresh
RUN pip install --no-cache-dir -r deps.txt

# Force-remove old groq versions (if stuck in cache)
RUN pip uninstall -y groq || true

# Install correct Groq SDK
RUN pip install --no-cache-dir groq==0.7.0

# Copy all application code
COPY . .

# Create data directory if missing
RUN mkdir -p data/docs

# Expose port
EXPOSE 5001

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.api.android_server:app", "--host", "0.0.0.0", "--port", "5001"]
