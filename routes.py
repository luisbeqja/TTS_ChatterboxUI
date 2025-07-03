from flask import Blueprint, render_template, request, jsonify, send_file, url_for
from config import Config
from utils import validate_filename, handle_error


def create_routes(tts_service):
    """Create and configure routes blueprint with TTS service dependency."""
    
    routes = Blueprint('routes', __name__)
    
    @routes.route('/')
    def index():
        """Main page with TTS interface."""
        try:
            audio_history = tts_service.get_audio_history()
            device_info = tts_service.get_device_info()
            return render_template('index.html', 
                                 audio_history=audio_history,
                                 device_info=device_info)
        except Exception as e:
            return handle_error(f"Error loading page: {str(e)}", 500)
    
    @routes.route('/voice-clone')
    def voice_clone():
        """Voice cloning page."""
        try:
            return render_template('voice_clone.html')
        except Exception as e:
            return handle_error(f"Error loading voice clone page: {str(e)}", 500)
    
    @routes.route('/save-voice-recording', methods=['POST'])
    def save_voice_recording():
        """Save voice recording for cloning."""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            if audio_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file type
            if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
                return jsonify({'error': 'Invalid file type. Please upload WAV, MP3, or M4A files.'}), 400
            
            # Generate unique filename
            import uuid
            import os
            from datetime import datetime
            
            filename = f"voice_clone_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            
            # Create voice_clone directory if it doesn't exist
            voice_clone_dir = os.path.join(Config.OUTPUT_DIR, 'voice_clone')
            os.makedirs(voice_clone_dir, exist_ok=True)
            
            filepath = os.path.join(voice_clone_dir, filename)
            
            # Save the file
            audio_file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'message': 'Voice recording saved successfully for cloning'
            })
            
        except Exception as e:
            return handle_error(f"Error saving voice recording: {str(e)}", 500)
    
    @routes.route('/voice-recordings')
    def list_voice_recordings():
        """List all saved voice recordings."""
        try:
            recordings = tts_service.get_available_voices()
            return jsonify({'recordings': recordings})
            
        except Exception as e:
            return handle_error(f"Error listing voice recordings: {str(e)}", 500)
    
    @routes.route('/available-voices')
    def get_available_voices():
        """Get available voices for TTS generation."""
        try:
            voices = tts_service.get_available_voices()
            return jsonify({'voices': voices})
            
        except Exception as e:
            return handle_error(f"Error getting available voices: {str(e)}", 500)
    
    @routes.route('/voice-recording/<filename>')
    def serve_voice_recording(filename):
        """Serve voice recording file."""
        try:
            # Validate filename for security
            if not validate_filename(filename):
                return "Invalid filename", 400
            
            import os
            voice_clone_dir = os.path.join(Config.OUTPUT_DIR, 'voice_clone')
            filepath = os.path.join(voice_clone_dir, filename)
            
            if not os.path.exists(filepath):
                return "Voice recording file not found", 404
            
            return send_file(filepath, mimetype=Config.AUDIO_MIMETYPE)
            
        except Exception as e:
            return handle_error(f"Error serving voice recording: {str(e)}", 500)
    
    @routes.route('/voice-recording/<filename>', methods=['DELETE'])
    def delete_voice_recording(filename):
        """Delete voice recording file."""
        try:
            # Validate filename for security
            if not validate_filename(filename):
                return jsonify({'error': 'Invalid filename'}), 400
            
            import os
            voice_clone_dir = os.path.join(Config.OUTPUT_DIR, 'voice_clone')
            filepath = os.path.join(voice_clone_dir, filename)
            
            if not os.path.exists(filepath):
                return jsonify({'error': 'Voice recording file not found'}), 404
            
            # Delete the file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': 'Voice recording deleted successfully'
            })
            
        except Exception as e:
            return handle_error(f"Error deleting voice recording: {str(e)}", 500)
    
    @routes.route('/upload-voice', methods=['POST'])
    def upload_voice():
        """Upload voice recording for cloning."""
        try:
            if 'audio' not in request.files:
                return jsonify({'error': 'No audio file provided'}), 400
            
            audio_file = request.files['audio']
            if audio_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Validate file type
            if not audio_file.filename.lower().endswith(('.wav', '.mp3', '.m4a')):
                return jsonify({'error': 'Invalid file type. Please upload WAV, MP3, or M4A files.'}), 400
            
            # Generate unique filename
            import uuid
            import os
            from datetime import datetime
            
            filename = f"voice_recording_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            filepath = os.path.join(Config.OUTPUT_DIR, filename)
            
            # Save the file
            audio_file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'message': 'Voice recording uploaded successfully'
            })
            
        except Exception as e:
            return handle_error(f"Error uploading voice recording: {str(e)}", 500)
    
    @routes.route('/generate', methods=['POST'])
    def generate_tts():
        """Generate TTS audio from text."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400
            
            text = data.get('text', '').strip()
            voice_file = data.get('voice_file', None)  # Optional voice file for cloning
            
            # Generate audio using TTS service
            result = tts_service.generate_audio(text, voice_file)
            
            if 'error' in result:
                return jsonify(result), 400
            
            # Add audio URL to result
            result['audio_url'] = url_for('routes.serve_audio', filename=result['filename'])
            
            return jsonify(result)
            
        except Exception as e:
            error_msg = f'Unexpected error during generation: {str(e)}'
            print(error_msg)
            return jsonify({'error': error_msg}), 500
    
    @routes.route('/audio/<filename>')
    def serve_audio(filename):
        """Serve audio file for playback."""
        try:
            # Validate filename for security
            if not validate_filename(filename):
                return "Invalid filename", 400
            
            if not tts_service.file_exists(filename):
                return "Audio file not found", 404
            
            filepath = tts_service.get_audio_filepath(filename)
            return send_file(filepath, mimetype=Config.AUDIO_MIMETYPE)
            
        except Exception as e:
            return handle_error(f"Error serving audio: {str(e)}", 500)
    
    @routes.route('/download/<filename>')
    def download_audio(filename):
        """Download audio file."""
        try:
            # Validate filename for security
            if not validate_filename(filename):
                return "Invalid filename", 400
            
            if not tts_service.file_exists(filename):
                return "Audio file not found", 404
            
            filepath = tts_service.get_audio_filepath(filename)
            return send_file(filepath, as_attachment=True, download_name=filename)
            
        except Exception as e:
            return handle_error(f"Error downloading audio: {str(e)}", 500)
    
    @routes.route('/status')
    def status():
        """Get service status and device information."""
        try:
            device_info = tts_service.get_device_info()
            history_count = len(tts_service.get_audio_history())
            
            return jsonify({
                'status': 'running',
                'device_info': device_info,
                'history_count': history_count,
                'max_text_length': Config.MAX_TEXT_LENGTH,
                'max_history_items': Config.MAX_HISTORY_ITEMS
            })
        except Exception as e:
            return handle_error(f"Error getting status: {str(e)}", 500)
    
    @routes.route('/health')
    def health():
        """Health check endpoint."""
        return jsonify({'status': 'healthy'}), 200
    
    return routes 