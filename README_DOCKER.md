# ChatterboxTTS Docker Deployment Guide

This guide explains how to deploy the ChatterboxTTS application using Docker for easy setup and consistent environments.

## 🐳 Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (included with Docker Desktop)
- At least 4GB of available RAM
- Internet connection for downloading the Hugging Face model

### Build and Run with Docker Compose

1. **Production deployment:**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d chatterbox-tts
   ```

2. **Development mode (with live code reloading):**
   ```bash
   docker-compose -f docker/docker-compose.yml --profile dev up chatterbox-tts-dev
   ```

3. **Access the application:**
   - Production: http://localhost:5000
   - Development: http://localhost:5001

## 🛠️ Docker Configuration

### Services

#### Production Service (`chatterbox-tts`)
- **Port:** 5000
- **Environment:** Production optimized
- **Volumes:** Persistent outputs and model cache
- **Memory:** 2-4GB allocated
- **Restart:** Automatic unless stopped

#### Development Service (`chatterbox-tts-dev`)
- **Port:** 5001
- **Environment:** Development mode with debug enabled
- **Volumes:** Live code mounting + persistent data
- **Restart:** Manual

### Volume Mounts

```yaml
volumes:
  - ./outputs:/app/outputs          # Generated audio files
  - ./cache:/app/cache              # Hugging Face model cache
  - ./voices:/app/voices:ro         # Custom voice samples (optional)
```

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Start production service
docker-compose -f docker/docker-compose.yml up -d chatterbox-tts

# View logs
docker-compose -f docker/docker-compose.yml logs -f chatterbox-tts

# Stop service
docker-compose -f docker/docker-compose.yml down
```

### Option 2: Docker Build and Run

```bash
# Build the image
docker build -f docker/Dockerfile -t chatterbox-tts .

# Run the container
docker run -d \
  --name chatterbox-tts-app \
  -p 5000:5000 \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/cache:/app/cache \
  -e PYTHONUNBUFFERED=1 \
  chatterbox-tts
```

### Option 3: Quick Run (Direct Docker Command)

For quick testing without Docker Compose:

```bash
# Run the development container directly
docker run --rm -p 5000:5000 --name chatterbox-tts docker-chatterbox-tts-dev
```

**Note:** This assumes you have already built the image. To build first:
```bash
docker build -f docker/Dockerfile -t docker-chatterbox-tts-dev .
```

### Option 4: Pre-load Model

To pre-download the ChatterboxTTS model during container startup:

```bash
docker-compose -f docker/docker-compose.yml up -d -e PRELOAD_MODEL=true chatterbox-tts
```

## 📁 Directory Structure

```
TTS_Tests/
├── deploy.sh               # Easy deployment script
├── README_DOCKER.md        # Docker deployment guide
├── docker/                 # Docker configuration files
│   ├── Dockerfile          # Main Docker configuration
│   ├── docker-compose.yml  # Multi-service orchestration
│   ├── docker-entrypoint.sh # Container startup script
│   └── .dockerignore       # Files excluded from build
├── outputs/                # Generated audio files (mounted)
├── cache/                  # Model cache (mounted)
├── voices/                 # Custom voice samples (optional)
└── ...
```

## ⚙️ Environment Variables

The following environment variables can be customized:

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_ENV` | production | Flask environment mode |
| `DEBUG` | False | Enable debug mode |
| `PYTHONUNBUFFERED` | 1 | Python output buffering |
| `HF_HOME` | /app/cache/huggingface | Hugging Face cache directory |
| `TRANSFORMERS_CACHE` | /app/cache/transformers | Transformers cache directory |
| `TORCH_HOME` | /app/cache/torch | PyTorch cache directory |
| `PRELOAD_MODEL` | false | Pre-download model on startup |

## 🔧 Customization

### Resource Limits

Adjust memory limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      memory: 6G        # Increase for better performance
    reservations:
      memory: 3G        # Minimum reserved memory
```

### Custom Configuration

Mount a custom config file:

```yaml
volumes:
  - ./custom_config.py:/app/src/config/config.py
```

### GPU Support (CUDA)

For NVIDIA GPU support, modify the `docker-compose.yml`:

```yaml
services:
  chatterbox-tts:
    # ... other configuration ...
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

## 🐛 Troubleshooting

### Common Issues

1. **Model Download Fails:**
   ```bash
   # Clear cache and restart
   docker-compose down
   sudo rm -rf cache/
   docker-compose up -d
   ```

2. **Permission Issues:**
   ```bash
   # Fix ownership of mounted volumes
   sudo chown -R $USER:$USER outputs/ cache/
   ```

3. **Memory Issues:**
   ```bash
   # Check container memory usage
   docker stats chatterbox-tts-app
   
   # Increase memory limit in docker-compose.yml
   ```

4. **Port Conflicts:**
   ```bash
   # Change port mapping in docker-compose.yml
   ports:
     - "5001:5000"  # Use different host port
   ```

### Debugging

```bash
# View application logs
docker-compose -f docker/docker-compose.yml logs -f chatterbox-tts

# Access container shell
docker-compose -f docker/docker-compose.yml exec chatterbox-tts bash

# Check container health
docker-compose -f docker/docker-compose.yml ps
```

## 📊 Performance Tips

1. **Use SSD storage** for model cache directory
2. **Allocate sufficient RAM** (minimum 4GB recommended)
3. **Enable GPU support** if available
4. **Persist model cache** to avoid re-downloading
5. **Use production mode** for better performance

## 🔒 Security Notes

- The container runs as a non-root user (`app`)
- Health checks are configured for monitoring
- Only necessary ports are exposed
- Model cache is isolated within container volumes

## 📦 Production Deployment

For production deployment, consider:

1. **Reverse Proxy:** Use nginx or traefik
2. **SSL/TLS:** Enable HTTPS
3. **Monitoring:** Add logging and metrics
4. **Backup:** Regular backup of outputs and cache
5. **Scaling:** Use Docker Swarm or Kubernetes

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🆘 Support

If you encounter issues:

1. Check the application logs
2. Verify system requirements
3. Ensure proper volume permissions
4. Review environment variables
5. Check Docker/Docker Compose versions

For development support, use the development container with mounted source code for easier debugging. 