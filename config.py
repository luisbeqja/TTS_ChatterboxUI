import torch

class Config:
    """Configuration settings for the TTS Flask application."""
    
    # Flask settings
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    
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