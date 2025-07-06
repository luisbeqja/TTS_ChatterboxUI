# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    libsox-dev \
    sox \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV HF_HOME=/app/cache/huggingface
ENV TRANSFORMERS_CACHE=/app/cache/transformers
ENV TORCH_HOME=/app/cache/torch

# Set pip configuration for better network resilience
ENV PIP_RETRIES=10
ENV PIP_TIMEOUT=30
ENV PIP_NO_CACHE_DIR=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with improved network handling
RUN pip install --upgrade pip && \
    pip install --retries 10 --timeout 60 --no-cache-dir torch torchaudio && \
    pip install --retries 10 --timeout 60 --no-cache-dir transformers huggingface-hub && \
    pip install --retries 10 --timeout 60 --no-cache-dir scipy scikit-learn && \
    pip install --retries 10 --timeout 60 --no-cache-dir librosa soundfile && \
    pip install --retries 10 --timeout 60 --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy Docker entrypoint script
COPY docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create necessary directories
RUN mkdir -p /app/outputs /app/cache /app/cache/huggingface /app/cache/transformers /app/cache/torch

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose the application port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Set the default command
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "app.py"] 