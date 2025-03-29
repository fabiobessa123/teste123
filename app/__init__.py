import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from dotenv import load_dotenv
from flask import Flask
from app.auth import auth_bp  # Importe os Blueprints aqui
from app.main import main_bp
from flask import Flask
from app.admin import admin_bp  # Agora deve ser reconhecido
from app.api import api_bp     # Idem
from flask import Flask
app = Flask(__name__)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
talisman = Talisman()

def create_app():
    app = Flask(__name__)
    
    # Configurações básicas
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'uploads/ebooks'
    app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'epub'}
    
    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    talisman.init_app(app, force_https=False)  # Habilitar em produção
    
    # Blueprints
   
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Configurações do Login
    login_manager.login_view = 'auth.login'
    
    return app