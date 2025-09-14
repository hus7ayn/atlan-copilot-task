# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt requirements-minimal.txt requirements-no-chromadb.txt .

# Upgrade pip and install Python dependencies with fallbacks
RUN pip install --upgrade pip setuptools wheel && \
    (pip install --no-cache-dir --timeout=1000 -r requirements.txt || \
     (echo "Failed to install with main requirements, trying without chromadb..." && \
      pip install --no-cache-dir --timeout=1000 -r requirements-no-chromadb.txt || \
      (echo "Failed to install without chromadb, trying minimal requirements..." && \
       pip install --no-cache-dir --timeout=1000 -r requirements-minimal.txt)))

# Copy application code
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Start the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
