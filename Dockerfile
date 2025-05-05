# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install pip dependencies with increased timeout
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --timeout 1000 torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --timeout 1000 -r requirements.txt

# Copy only necessary code
COPY proto/ proto/
COPY server/ server/

# Create models directory (models will be mounted)
RUN mkdir -p /app/backend/models/voice_model/music

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/backend/models

# Expose gRPC port
EXPOSE 50051

# Command to run the server
CMD ["python", "server/server.py"] 