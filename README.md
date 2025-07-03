# ChatterboxTTS Web Application

A modern Flask web interface for text-to-speech (TTS) generation using ChatterboxTTS.

## Features
- Convert text to speech using a web interface
- Voice cloning: upload or record your own voice for custom TTS
- Audio history and download

## Requirements
- Python 3.8+
- (Recommended) Virtual environment (venv, conda, etc.)

## Installation
1. **Clone the repository** (if not already):
   ```bash
   git clone <repo-url>
   cd TTS_Tests
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
1. **Start the Flask app:**
   ```bash
   python app.py
   ```
2. **Access the web interface:**
   Open your browser and go to: [http://localhost:5000](http://localhost:5000)

## Usage
- **Text-to-Speech:** Enter text on the main page and click "Generate" to create speech audio.
- **Voice Cloning:** Go to the "Voice Clone" page, record or upload a voice sample, then use it for TTS.
- **Audio History:** Listen to or download previously generated audio from the main page.

## Configuration
- Default settings (host, port, output directory, etc.) can be changed in `config.py`.
- Outputs are saved in the `outputs/` directory (created automatically).

## Notes
- The TTS model will load on the first request (may take a few seconds).
- For best performance, use a machine with a GPU (CUDA or Apple MPS supported).

## Troubleshooting
- If you encounter errors related to device or model loading, check your PyTorch and hardware setup.
- For issues with dependencies, try updating pip: `pip install --upgrade pip`.

---

Enjoy using ChatterboxTTS! 🎤 