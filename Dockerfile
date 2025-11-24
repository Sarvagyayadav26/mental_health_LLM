# Force rebuild on every deploy
ARG CACHEBUST=1

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements with cache-bust
ARG CACHEBUST
COPY requirements1.txt requirements1.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements1.txt

# Copy all project files with cache-bust
ARG CACHEBUST
COPY . .

# Remove any old Groq versions
RUN rm -rf /usr/local/lib/python3.11/site-packages/groq || true
RUN rm -rf /usr/local/lib/python3.11/site-packages/groq-*.dist-info || true
RUN pip uninstall -y groq || true
RUN pip uninstall -y groq || true

# Install stable Groq
RUN pip install --no-cache-dir groq==0.5.0

RUN mkdir -p data/docs

EXPOSE 5001

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health')" || exit 1

CMD ["python", "-m", "uvicorn", "src.api.android_server:app", "--host", "0.0.0.0", "--port", "5001"]
