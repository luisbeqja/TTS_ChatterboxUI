#!/bin/bash
set -e

echo "Starting ChatterboxTTS application..."

# Create directories if they don't exist
mkdir -p /app/outputs /app/cache

# Note: Ownership is already set correctly by Docker build process

# Optional: Pre-download the model if not cached
if [ "$PRELOAD_MODEL" = "true" ]; then
    echo "Pre-loading ChatterboxTTS model..."
    python -c "
from chatterbox.tts import ChatterboxTTS
import torch
print('Downloading ChatterboxTTS model...')
model = ChatterboxTTS.from_pretrained(device='cpu')
print('Model downloaded and cached successfully!')
"
fi

# Start the application
echo "Starting Flask application..."
exec "$@" 