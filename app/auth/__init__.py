from flask import Blueprint

# Crie o Blueprint primeiro
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Importe as rotas DEPOIS para evitar imports circulares
from app.auth import routes