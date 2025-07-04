import torch

class Config:
    """Configuration settings for the TTS Flask application."""
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
    # Model loading settings
    LAZY_LOAD_MODEL = False  # Set to True for faster startup, False for faster first request
    USE_RELOADER = False     # Set to True for development auto-reload, False to keep model in memory
    
    # TTS settings
    MAX_TEXT_LENGTH = 1000
    MAX_HISTORY_ITEMS = 20
    OUTPUT_DIR = 'outputs'
    
    # Audio settings
    AUDIO_FORMAT = 'wav'
    AUDIO_MIMETYPE = 'audio/wav'
    
    # TTS generation parameters
    DEFAULT_CFG_WEIGHT = 0.3  # Lower CFG weight for faster generation
    DEFAULT_EXAGGERATION = 0.5  # Balanced exaggeration
    
    # Streaming TTS settings
    STREAMING_ENABLED = True
    STREAMING_CHUNK_SIZE = 200  # Maximum characters per chunk
    STREAMING_MIN_CHUNK_SIZE = 50  # Minimum characters per chunk
    STREAMING_MAX_CONCURRENT_CHUNKS = 3  # Maximum chunks to process concurrently
    STREAMING_PRELOAD_CHUNKS = 2  # Number of chunks to preload
    STREAMING_TIMEOUT = 30  # Timeout for streaming sessions in seconds
    
    # Audio streaming settings
    AUDIO_CHUNK_BUFFER_SIZE = 1024 * 16  # Buffer size for audio streaming
    AUDIO_OVERLAP_MS = 50  # Overlap between audio chunks in milliseconds


class DeviceConfig:
    """Device detection and optimization configuration."""
    
    @staticmethod
    def detect_device():
        """Detect the best available device for PyTorch."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    @staticmethod
    def setup_device_optimizations(device):
        """Setup device-specific optimizations."""
        if device == "mps":
            torch.backends.mps.allow_fp16 = True
            print("MPS optimizations enabled")
        elif device == "cuda":
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.enabled = True
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
            print("CUDA optimizations enabled")
        
        # Disable gradients for inference
        torch.set_grad_enabled(False)
        print(f"Using device: {device}")
        return device 