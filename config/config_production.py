import torch
import os

class Config:
    """Production configuration settings for the TTS Flask application."""
    
    # Flask settings
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
    
    # Model loading settings
    LAZY_LOAD_MODEL = True   # Faster startup for production
    USE_RELOADER = False     # Never reload in production
    
    # TTS settings
    MAX_TEXT_LENGTH = 1000
    MAX_HISTORY_ITEMS = 50   # More history for production
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'outputs')
    
    # Audio settings
    AUDIO_FORMAT = 'wav'
    AUDIO_MIMETYPE = 'audio/wav'
    
    # TTS generation parameters - optimized for production
    DEFAULT_CFG_WEIGHT = 0.3
    DEFAULT_EXAGGERATION = 0.5
    
    # Performance settings
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS', 4))
    WORKER_TIMEOUT = int(os.environ.get('WORKER_TIMEOUT', 120))
    
    # File cleanup settings
    CLEANUP_INTERVAL_HOURS = int(os.environ.get('CLEANUP_INTERVAL_HOURS', 24))
    MAX_FILE_AGE_HOURS = int(os.environ.get('MAX_FILE_AGE_HOURS', 48))


class DeviceConfig:
    """Device detection and optimization configuration for production."""
    
    @staticmethod
    def detect_device():
        """Detect the best available device for PyTorch."""
        # Force device from environment if specified
        forced_device = os.environ.get('FORCE_DEVICE')
        if forced_device:
            return forced_device
            
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    @staticmethod
    def setup_device_optimizations(device):
        """Setup device-specific optimizations for production."""
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
        
        # Set number of threads for CPU inference
        if device == "cpu":
            num_threads = int(os.environ.get('OMP_NUM_THREADS', 4))
            torch.set_num_threads(num_threads)
            print(f"CPU threads set to: {num_threads}")
        
        print(f"Using device: {device}")
        return device 