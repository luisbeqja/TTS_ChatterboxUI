import torch
import torchaudio as ta
import time
import uuid
import os
from datetime import datetime
from chatterbox.tts import ChatterboxTTS
from config import Config, DeviceConfig


class TTSService:
    """Text-to-Speech service handling model loading and audio generation."""
    
    def __init__(self, lazy_load=False):
        self.model = None
        self.device = None
        self.audio_history = []
        self._model_loaded = False
        self._lazy_load = lazy_load
        
        if not lazy_load:
            self._initialize()
        else:
            # Just setup device and create output directory
            self._setup_device_only()
            self._create_output_dir()
    
    def _initialize(self):
        """Initialize the TTS service with device detection and model loading."""
        self._setup_device_only()
        self._create_output_dir()
        self._load_model()
    
    def _setup_device_only(self):
        """Setup device detection and optimizations without loading the model."""
        self.device = DeviceConfig.detect_device()
        self.device = DeviceConfig.setup_device_optimizations(self.device)
    
    def _create_output_dir(self):
        """Create output directory if it doesn't exist."""
        os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    
    def _ensure_model_loaded(self):
        """Ensure the model is loaded (lazy loading)."""
        if not self._model_loaded:
            print("Loading ChatterboxTTS model (first request)...")
            self._load_model()
            self._model_loaded = True
    
    def _load_model(self):
        """Load the ChatterboxTTS model with fallback handling."""
        if not self._lazy_load:
            print("Loading ChatterboxTTS model...")
        
        start_time = time.time()
        
        try:
            self.model = ChatterboxTTS.from_pretrained(device=self.device)
            print(f"Model loaded successfully on {self.device}")
        except Exception as e:
            if self.device == "mps" and "Output channels > 65536 not supported" in str(e):
                print(f"MPS device limitation detected. Falling back to CPU...")
                self.device = "cpu"
                torch.set_grad_enabled(False)  # Re-disable gradients for CPU
                self.model = ChatterboxTTS.from_pretrained(device=self.device)
                print(f"Model loaded successfully on CPU (MPS fallback)")
            else:
                raise e
        
        load_time = time.time() - start_time
        print(f"Model loaded in {load_time:.2f} seconds on {self.device}")
        self._model_loaded = True
    
    def generate_audio(self, text, voice_file=None):
        """
        Generate audio from text with error handling and device fallback.
        
        Args:
            text (str): Text to convert to speech
            voice_file (str, optional): Path to voice recording for cloning
            
        Returns:
            dict: Generation result with audio info or error
        """
        if not text or not text.strip():
            return {'error': 'Please provide text to convert'}
        
        if len(text) > Config.MAX_TEXT_LENGTH:
            return {'error': f'Text too long. Maximum {Config.MAX_TEXT_LENGTH} characters.'}
        
        # Ensure model is loaded (lazy loading)
        self._ensure_model_loaded()
        
        print(f"Generating audio for: '{text}'")
        generation_start = time.time()
        
        try:
            # Generate unique filename
            audio_id = str(uuid.uuid4())
            filename = f"audio_{audio_id}.{Config.AUDIO_FORMAT}"
            filepath = os.path.join(Config.OUTPUT_DIR, filename)
            
            # Generate audio with fallback handling
            wav = self._generate_with_fallback(text, voice_file)
            
            # Save audio file
            ta.save(filepath, wav, self.model.sr)
            generation_time = time.time() - generation_start
            
            # Create audio entry
            audio_entry = {
                'id': audio_id,
                'text': text,
                'filename': filename,
                'filepath': filepath,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'generation_time': f"{generation_time:.2f}s"
            }
            
            # Add to history and manage cleanup
            self._add_to_history(audio_entry)
            
            print(f"Audio generated in {generation_time:.2f} seconds")
            
            return {
                'success': True,
                'audio_id': audio_id,
                'filename': filename,
                'generation_time': generation_time,
                'filepath': filepath
            }
            
        except Exception as e:
            error_msg = f'Generation failed: {str(e)}'
            print(f"Error generating TTS: {error_msg}")
            return {'error': error_msg}
    
    def _generate_with_fallback(self, text, voice_file=None):
        """Generate audio with MPS fallback handling."""
        with torch.no_grad():
            try:
                # Prepare generation parameters
                gen_params = {
                    'text': text,
                    'cfg_weight': Config.DEFAULT_CFG_WEIGHT,
                    'exaggeration': Config.DEFAULT_EXAGGERATION
                }
                
                # Add voice file if provided
                if voice_file and os.path.exists(voice_file):
                    gen_params['audio_prompt_path'] = voice_file
                    print(f"Using voice cloning with: {voice_file}")
                
                wav = self.model.generate(**gen_params)
                return wav
            except RuntimeError as e:
                if "Output channels > 65536 not supported" in str(e):
                    print(f"MPS limitation during generation. Moving model to CPU...")
                    self.device = "cpu"
                    # Recreate the model on CPU instead of using .to()
                    self.model = ChatterboxTTS.from_pretrained(device=self.device)
                    
                    # Retry generation with same parameters
                    wav = self.model.generate(**gen_params)
                    print(f"Generation completed on CPU (MPS fallback)")
                    return wav
                else:
                    raise e
    
    def _add_to_history(self, audio_entry):
        """Add audio entry to history and manage cleanup."""
        self.audio_history.insert(0, audio_entry)  # Add to beginning
        
        # Keep only last N entries and cleanup old files
        if len(self.audio_history) > Config.MAX_HISTORY_ITEMS:
            old_entry = self.audio_history.pop()
            if os.path.exists(old_entry['filepath']):
                try:
                    os.remove(old_entry['filepath'])
                except OSError as e:
                    print(f"Warning: Could not remove old audio file {old_entry['filepath']}: {e}")
    
    def get_audio_history(self):
        """Get the current audio generation history."""
        return self.audio_history
    
    def get_audio_filepath(self, filename):
        """Get the full filepath for an audio file."""
        return os.path.join(Config.OUTPUT_DIR, filename)
    
    def file_exists(self, filename):
        """Check if an audio file exists."""
        filepath = self.get_audio_filepath(filename)
        return os.path.exists(filepath)
    
    def get_device_info(self):
        """Get current device information."""
        return {
            'device': self.device,
            'model_loaded': self._model_loaded,
            'cuda_available': torch.cuda.is_available(),
            'mps_available': torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
        }
    
    def get_available_voices(self):
        """Get list of available voice recordings for cloning."""
        voice_clone_dir = os.path.join(Config.OUTPUT_DIR, 'voice_clone')
        
        if not os.path.exists(voice_clone_dir):
            return []
        
        voices = []
        for filename in os.listdir(voice_clone_dir):
            if filename.lower().endswith(('.wav', '.mp3', '.m4a')):
                filepath = os.path.join(voice_clone_dir, filename)
                stat = os.stat(filepath)
                voices.append({
                    'filename': filename,
                    'filepath': filepath,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        # Sort by creation time, newest first
        voices.sort(key=lambda x: x['created'], reverse=True)
        return voices 