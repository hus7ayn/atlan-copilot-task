# Use Python 3.9 slim image
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy client package files and install Node dependencies
COPY client/package*.json ./client/
WORKDIR /app/client
RUN npm install

# Copy the rest of the application
WORKDIR /app
COPY . .

# Build React app
WORKDIR /app/client
RUN npm run build

# Return to app root
WORKDIR /app

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV PYTHONPATH=/app

# Start the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
