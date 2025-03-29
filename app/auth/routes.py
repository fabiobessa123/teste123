from app.auth import auth_bp  # Importe o blueprint criado
from flask import render_template

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')