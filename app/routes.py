from flask import Blueprint, render_template
from app.extensions import db
from app.models import Ebook

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    ebooks = db.session.query(Ebook).all()
    return render_template('index.html', ebooks=ebooks)

@main_bp.route('/upload')
def upload():
    return render_template('upload.html')