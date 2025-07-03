"""
ChatterboxTTS Flask Web Application

A modern web interface for text-to-speech generation using ChatterboxTTS.
This is the main application entry point that initializes all components.
"""

from flask import Flask
from config import Config
from services.tts_service import TTSService
from routes import create_routes
from utils import cleanup_temp_files
import atexit


def create_app():
    """
    Application factory function to create and configure the Flask app.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Configure Flask app
    app.config.from_object(Config)
    
    return app


def initialize_services():
    """
    Initialize all services required by the application.
    This function is now used for cleanup only.
    """
    # Clean up any leftover files on startup
    cleanup_temp_files()


def register_routes(app, tts_service):
    """
    Register all routes with the Flask app.
    
    Args:
        app (Flask): Flask application instance
        tts_service (TTSService): TTS service instance
    """
    routes_blueprint = create_routes(tts_service)
    app.register_blueprint(routes_blueprint)


def setup_cleanup_handlers(tts_service):
    """
    Setup cleanup handlers for graceful shutdown.
    
    Args:
        tts_service (TTSService): TTS service instance
    """
    def cleanup():
        print("Performing cleanup on shutdown...")
        cleanup_temp_files()
        print("Cleanup completed.")
    
    atexit.register(cleanup)


def main():
    """Main application entry point."""
    try:
        # Create Flask app
        app = create_app()
        
        # Initialize cleanup
        initialize_services()
        
        # Create TTS service with lazy loading (model loads on first request)
        tts_service = TTSService(lazy_load=True)
        
        # Register routes
        register_routes(app, tts_service)
        
        # Setup cleanup handlers
        setup_cleanup_handlers(tts_service)
        
        print(f"\n{'='*50}")
        print("🎤 ChatterboxTTS Web Application")
        print(f"{'='*50}")
        print(f"Server: http://{Config.HOST}:{Config.PORT}")
        print(f"Debug mode: {Config.DEBUG}")
        print(f"Max text length: {Config.MAX_TEXT_LENGTH} characters")
        print(f"Output directory: {Config.OUTPUT_DIR}/")
        print("Model will load on first request...")
        print(f"{'='*50}\n")
        
        # Run the application
        app.run(
            debug=Config.DEBUG,
            host=Config.HOST,
            port=Config.PORT,
            threaded=True,  # Enable threading for better performance
            use_reloader=True  # Keep auto-reload for development
        )
        
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Failed to start application: {e}")
        raise


if __name__ == '__main__':
    main()