# force-rebuild-v9

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy NEW requirements file FIRST
COPY requirements1.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements1.txt

# --- IMPORTANT: DO NOT PUT GROQ FIX HERE ---
# (This part stays cached if placed before COPY . .)

# Copy project files (FORCE new layer → breaks cache)
COPY . .

# ⬇️⬇️⬇️ NOW INSERT THE GROQ FIX BLOCK HERE ⬇️⬇️⬇️

# Remove old Groq library completely
RUN rm -rf /usr/local/lib/python3.11/site-packages/groq || true
RUN rm -rf /usr/local/lib/python3.11/site-packages/groq-*.dist-info || true

# Uninstall any cached pip Groq versions
RUN pip uninstall -y groq || true
RUN pip uninstall -y groq || true

# Install the correct stable version
RUN pip install --no-cache-dir groq==0.6.0

# ⬆️⬆️⬆️ END GROQ FIX BLOCK ⬆️⬆️⬆️

# Create data directory
RUN mkdir -p data/docs

# Expose port
EXPOSE 5001

# Env variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health')" || exit 1

# Start server
CMD ["python", "-m", "uvicorn", "src.api.android_server:app", "--host", "0.0.0.0", "--port", "5001"]
