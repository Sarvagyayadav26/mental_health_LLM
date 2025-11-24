# force-rebuild-v8

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy NEW requirements1 file
COPY requirements1.txt .

RUN pip install --upgrade pip

# Install all dependencies
RUN pip install --no-cache-dir -r requirements1.txt


# ⬇️⬇️⬇️ INSERT BLOCK HERE (JUST AFTER REQUIREMENTS INSTALL) ⬇️⬇️⬇️

# 🔥 HARD DELETE ANY EXISTING GROQ LIB FILES
RUN rm -rf /usr/local/lib/python3.11/site-packages/groq || true
RUN rm -rf /usr/local/lib/python3.11/site-packages/groq-*.dist-info || true

# Uninstall any pip groq versions
RUN pip uninstall -y groq || true
RUN pip uninstall -y groq || true

# Install ONLY correct version
RUN pip install --no-cache-dir groq==0.6.0

# ⬆️⬆️⬆️ END OF INSERTED BLOCK ⬆️⬆️⬆️


# Copy all application code
COPY . .

RUN mkdir -p data/docs

EXPOSE 5001

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5001/health')" || exit 1

CMD ["python", "-m", "uvicorn", "src.api.android_server:app", "--host", "0.0.0.0", "--port", "5001"]
