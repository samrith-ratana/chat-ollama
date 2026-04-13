from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from .config import Config
from .routes import api_bp
from ..services.ollama_service import OllamaService
from ..services.knowledge_service import KnowledgeService
from ..services.chat_service import ChatService

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)
    
    # Initialize config
    config_class.init_app(app)
    
    # Initialize services
    ollama_service = OllamaService(app.config['OLLAMA_BASE_URL'])
    knowledge_service = KnowledgeService(app.config['KNOWLEDGE_DB_PATH'])
    chat_service = ChatService(
        ollama_service, 
        knowledge_service, 
        max_context_length=app.config['MAX_CONTEXT_LENGTH'],
        num_docs=app.config['NUM_RETRIEVED_DOCS']
    )
    
    # Register services in app config for routes to access
    app.config['OLLAMA_SERVICE'] = ollama_service
    app.config['KNOWLEDGE_SERVICE'] = knowledge_service
    app.config['CHAT_SERVICE'] = chat_service
    app.config['DEFAULT_MODEL'] = app.config['DEFAULT_MODEL']
    app.config['ENABLE_RAG'] = app.config['ENABLE_RAG']
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Set the path to the web folder (static files)
    WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
    
    @app.route('/')
    def index():
        return send_from_directory(WEB_DIR, 'index.html')

    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory(WEB_DIR, path)
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.DEBUG)
