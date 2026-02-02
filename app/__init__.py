from flask import Flask, send_from_directory
from .config import Config
from .extensions import db, migrate, jwt, login_manager, cors
import os


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Configure login manager
    login_manager.login_view = 'admin.login'
    login_manager.login_message_category = 'info'

    # Initialize Firebase
    from .services.firebase_service import FirebaseService
    FirebaseService.initialize()

    # Import models so Flask-Migrate can detect them
    from .models import User, Classe, Student, Subject, Material, Payment, Attendance

    # Register blueprints
    from .api import api_bp
    from .admin import admin_bp

    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(upload_folder, filename)

    # Create uploads folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(os.path.join(upload_folder, 'materials'), exist_ok=True)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
