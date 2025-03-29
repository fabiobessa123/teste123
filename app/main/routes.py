from flask import render_template
from app.main import main_bp
from app.models import Ebook

@main_bp.route('/')
def index():
    ebooks = Ebook.query.all()
    return render_template('index.html', ebooks=ebooks)