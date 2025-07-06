import os
import re
import uuid
from datetime import datetime
from flask import jsonify

# Import configuration using relative imports
from .config.config import Config


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


def split_text_into_chunks(text, max_chunk_size=200):
    """
    Split text into logical chunks for streaming TTS.
    
    Args:
        text (str): Input text to split
        max_chunk_size (int): Maximum characters per chunk
        
    Returns:
        List[str]: List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Clean up text
    text = text.strip()
    
    # First, try to split by sentences
    sentences = re.split(r'([.!?]+)', text)
    chunks = []
    current_chunk = ""
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i].strip()
        
        # Skip empty sentences
        if not sentence:
            i += 1
            continue
            
        # Add punctuation back if it exists
        if i + 1 < len(sentences) and sentences[i + 1].strip() in ['.', '!', '?', '...']:
            sentence += sentences[i + 1].strip()
            i += 1
        
        # Check if adding this sentence would exceed max_chunk_size
        if len(current_chunk) + len(sentence) > max_chunk_size:
            # If current chunk is not empty, save it
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If sentence itself is too long, split it by commas or phrases
            if len(sentence) > max_chunk_size:
                sub_chunks = split_long_sentence(sentence, max_chunk_size)
                chunks.extend(sub_chunks)
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
        
        i += 1
    
    # Add remaining chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Remove empty chunks and return
    return [chunk for chunk in chunks if chunk.strip()]


def split_long_sentence(sentence, max_size=200):
    """
    Split a long sentence into smaller chunks based on commas and phrases.
    
    Args:
        sentence (str): Long sentence to split
        max_size (int): Maximum characters per chunk
        
    Returns:
        List[str]: List of sentence chunks
    """
    if len(sentence) <= max_size:
        return [sentence]
    
    # Try splitting by commas first
    parts = re.split(r'([,;:])', sentence)
    chunks = []
    current_chunk = ""
    
    i = 0
    while i < len(parts):
        part = parts[i].strip()
        
        if not part:
            i += 1
            continue
        
        # Add punctuation back if it exists
        if i + 1 < len(parts) and parts[i + 1].strip() in [',', ';', ':']:
            part += parts[i + 1].strip()
            i += 1
        
        if len(current_chunk) + len(part) > max_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If part is still too long, split by words
            if len(part) > max_size:
                word_chunks = split_by_words(part, max_size)
                chunks.extend(word_chunks)
            else:
                current_chunk = part
        else:
            current_chunk += " " + part if current_chunk else part
        
        i += 1
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if chunk.strip()]


def split_by_words(text, max_size=200):
    """
    Split text by words as last resort.
    
    Args:
        text (str): Text to split
        max_size (int): Maximum characters per chunk
        
    Returns:
        List[str]: List of word chunks
    """
    words = text.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        if len(current_chunk) + len(word) + 1 > max_size:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = ""
        
        current_chunk += " " + word if current_chunk else word
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return [chunk for chunk in chunks if chunk.strip()]


def estimate_audio_duration(text, words_per_minute=150):
    """
    Estimate audio duration based on text length.
    
    Args:
        text (str): Text to estimate duration for
        words_per_minute (int): Average speaking rate
        
    Returns:
        float: Estimated duration in seconds
    """
    word_count = len(text.split())
    return (word_count / words_per_minute) * 60


def generate_stream_id():
    """Generate a unique stream ID for tracking streaming sessions."""
    return str(uuid.uuid4())


def validate_stream_chunk(chunk_text, max_length=300):
    """
    Validate a text chunk for streaming TTS.
    
    Args:
        chunk_text (str): Text chunk to validate
        max_length (int): Maximum allowed length
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not chunk_text or not chunk_text.strip():
        return False
    
    if len(chunk_text) > max_length:
        return False
    
    return True 