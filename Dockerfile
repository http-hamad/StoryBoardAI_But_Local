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

# Create all necessary model directories and cache directory
RUN mkdir -p /app/backend/models/text_model/txt_models/meta-llama/Llama-3.2-1B && \
    mkdir -p /app/backend/models/text_model/txt_tokenizers/meta-llama/Llama-3.2-1B && \
    mkdir -p /app/backend/models/image_model/amused_model && \
    mkdir -p /app/backend/models/voice_model/tts_models/speecht5_tts && \
    mkdir -p /app/backend/models/voice_model/tts_processors/speecht5_tts && \
    mkdir -p /app/backend/models/voice_model/tts_vocoders/speecht5_hifigan && \
    mkdir -p /app/backend/models/voice_model/music && \
    mkdir -p /root/.cache/huggingface && \
    chmod -R 777 /root/.cache/huggingface

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_PATH=/app/backend/models
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface/transformers
ENV HF_DATASETS_CACHE=/root/.cache/huggingface/datasets

# Expose gRPC port
EXPOSE 50051

# Command to run the server
CMD ["python", "server/server.py"] 