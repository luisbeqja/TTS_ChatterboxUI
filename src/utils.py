import os
import re
import sys
from flask import jsonify

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import Config


def validate_filename(filename):
    """
    Validate filename for security purposes.
    
    Args:
        filename (str): Filename to validate
        
    Returns:
        bool: True if filename is valid and safe
    """
    if not filename:
        return False
    
    # Check for basic security issues
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check if it's a valid audio filename
    if not filename.endswith(f'.{Config.AUDIO_FORMAT}'):
        return False
    
    # Check filename pattern (audio_uuid.wav)
    pattern = r'^audio_[a-f0-9-]{36}\.wav$'
    return bool(re.match(pattern, filename))


def handle_error(message, status_code=500):
    """
    Handle errors consistently across the application.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        
    Returns:
        tuple: JSON response and status code
    """
    print(f"Error [{status_code}]: {message}")
    return jsonify({'error': message}), status_code


def sanitize_text(text):
    """
    Sanitize input text for TTS processing.
    
    Args:
        text (str): Input text
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove or replace problematic characters
    # You can expand this based on your TTS model requirements
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    
    return text


def get_audio_info(filepath):
    """
    Get information about an audio file.
    
    Args:
        filepath (str): Path to audio file
        
    Returns:
        dict: Audio file information
    """
    try:
        if not os.path.exists(filepath):
            return None
        
        stat = os.stat(filepath)
        return {
            'size': stat.st_size,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'exists': True
        }
    except Exception as e:
        print(f"Error getting audio info for {filepath}: {e}")
        return None


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def cleanup_temp_files():
    """
    Clean up any temporary files that might be left over.
    This can be called periodically or on app startup.
    """
    try:
        output_dir = Config.OUTPUT_DIR
        if not os.path.exists(output_dir):
            return
        
        # Get all audio files
        audio_files = [f for f in os.listdir(output_dir) 
                      if f.endswith(f'.{Config.AUDIO_FORMAT}')]
        
        # If there are more files than the max allowed, remove oldest ones
        if len(audio_files) > Config.MAX_HISTORY_ITEMS:
            # Sort by creation time
            audio_files.sort(key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
            
            # Remove oldest files
            files_to_remove = audio_files[:-Config.MAX_HISTORY_ITEMS]
            for filename in files_to_remove:
                try:
                    filepath = os.path.join(output_dir, filename)
                    os.remove(filepath)
                    print(f"Cleaned up old audio file: {filename}")
                except OSError as e:
                    print(f"Warning: Could not remove file {filename}: {e}")
    
    except Exception as e:
        print(f"Error during cleanup: {e}")


def validate_text_input(text):
    """
    Validate text input for TTS generation.
    
    Args:
        text (str): Input text to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Please provide text to convert"
    
    if len(text) > Config.MAX_TEXT_LENGTH:
        return False, f"Text too long. Maximum {Config.MAX_TEXT_LENGTH} characters allowed."
    
    # Check for potentially problematic content
    if len(text.strip()) < 1:
        return False, "Text is too short"
    
    return True, None 