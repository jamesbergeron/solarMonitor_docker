FROM python:3.11-slim

WORKDIR /app

# Copy requirements first
COPY requirements.txt .


# Install system dependencies + pip build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    supervisor \
    iputils-ping \
    procps \
    snmp \
 && pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt \
 && apt-get purge -y --auto-remove build-essential python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy app folder
COPY app/ ./app/

# Expose port if needed (for FastAPI)
EXPOSE 8090

COPY supervisord.conf /etc/supervisor/supervisord.conf

# Run supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]

