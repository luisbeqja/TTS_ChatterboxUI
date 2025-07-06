# ChatterboxTTS Web Application

A modern web interface for text-to-speech generation using ChatterboxTTS from Hugging Face.

## 🎤 Features

- **Text-to-Speech Generation**: Convert text to natural-sounding speech
- **Voice Cloning**: Upload voice samples for personalized speech generation
- **Modern Web Interface**: Clean, responsive UI for easy interaction
- **Multiple Device Support**: Automatic detection of CUDA, MPS, or CPU
- **Audio History**: Keep track of generated audio files
- **Real-time Generation**: Fast audio generation with optimized settings

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

The easiest way to get started:

```bash
# First time setup
./deploy.sh setup

# Start the application
./deploy.sh start

# Access at http://localhost:5000
```

For detailed Docker instructions, see the [Docker README](README_DOCKER.md).

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 📁 Project Structure

```
TTS_Tests/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── deploy.sh              # Docker deployment script
├── README_DOCKER.md       # Docker deployment guide
├── docker/                # Docker configuration files
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .dockerignore
│   └── docker-entrypoint.sh
├── src/                   # Application source code
│   ├── config/
│   │   └── config.py      # Configuration settings
│   ├── services/
│   │   └── tts_service.py # TTS service implementation
│   ├── templates/         # HTML templates
│   ├── routes.py          # Flask routes
│   └── utils.py           # Utility functions
├── outputs/               # Generated audio files
└── cache/                 # Model cache directory
```

## 🔧 Configuration

Key configuration options in `src/config/config.py`:

- `LAZY_LOAD_MODEL`: Load model on first request (faster startup)
- `MAX_TEXT_LENGTH`: Maximum text length for generation
- `DEFAULT_CFG_WEIGHT`: CFG weight for generation quality
- `OUTPUT_DIR`: Directory for generated audio files

## 🐳 Docker Deployment

This project is optimized for Docker deployment with:

- **Persistent model caching** to avoid re-downloading
- **Volume mounts** for generated audio files
- **Health checks** for monitoring
- **Development and production** configurations

See [README_DOCKER.md](README_DOCKER.md) for complete deployment instructions.

## 🎯 Usage

1. **Text Generation**: Enter text and click "Generate Audio"
2. **Voice Cloning**: Upload a voice sample and enter text
3. **Audio History**: View and download previously generated audio
4. **Settings**: Adjust generation parameters as needed

## 🛠️ Development

For local development:

```bash
# Install in development mode
pip install -r requirements.txt

# Run with debug enabled
python app.py
```

For Docker development:

```bash
# Start development container with live reloading
./deploy.sh dev
```

## 📊 Performance Tips

- Use Docker for consistent performance
- Enable GPU support if available
- Persist model cache to avoid re-downloading
- Use production mode for better performance

## 🆘 Troubleshooting

Common issues and solutions:

1. **Model loading issues**: Clear cache and restart
2. **Memory errors**: Increase Docker memory limits
3. **Port conflicts**: Change port in configuration
4. **Permission issues**: Check volume mount permissions

For more detailed troubleshooting, see the [Docker README](README_DOCKER.md).

## 🏗️ Built With

- **ChatterboxTTS**: Hugging Face text-to-speech model
- **Flask**: Web framework
- **PyTorch**: Deep learning framework
- **Docker**: Containerization
- **Bootstrap**: Frontend styling

## 📄 License

This project is licensed under the MIT License. 