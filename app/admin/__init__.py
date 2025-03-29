from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.admin import routes  # Importe as rotas após criar o Blueprint