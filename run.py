import os
import uuid
import urllib.parse
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mercadopago
from faker import Faker
from flask_migrate import Migrate
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, FileField
from wtforms.validators import DataRequired
from flask import Flask
from app.main import main_bp
from app import create_app
app = Flask(__name__)
app.register_blueprint(main_bp)
class EbookForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    price = FloatField('Preço', validators=[DataRequired()])
    ebook_file = FileField('Arquivo do Ebook', validators=[DataRequired()])

# Configuração inicial
env_path = Path(__file__).parent / 'dbenv.env'
load_dotenv(dotenv_path=env_path, override=True)

# Verificação de variáveis essenciais
required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME', 'SECRET_KEY', 'MERCADOPAGO_ACCESS_TOKEN']
missing = [var for var in required_vars if not os.getenv(var)]
if missing:
    raise ValueError(f"Variáveis faltando no .env: {missing}")

# Inicialização do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configuração do banco de dados com codificação segura
db_password = os.getenv('DB_PASSWORD', '')
encoded_password = urllib.parse.quote_plus(db_password.encode('utf-8').decode('utf-8'))

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:"
    f"{encoded_password}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}"
    f"/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de uploads
UPLOAD_FOLDER = 'uploads/ebooks'
ALLOWED_EXTENSIONS = {'pdf', 'epub'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Extensões
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
sdk = mercadopago.SDK(os.getenv('MERCADOPAGO_ACCESS_TOKEN'))
migrate = Migrate(app, db)

# Modelos
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Ebook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    cover_image = db.Column(db.String(200), default='default.jpg')
    file_path = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# Configuração do Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Acesso não autorizado', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Rotas
@app.route('/')
def index():
    ebooks = Ebook.query.all()
    return render_template('index.html', ebooks=ebooks)

@app.route('/ebook/<int:ebook_id>')
def ebook_detail(ebook_id):
    ebook = Ebook.query.get_or_404(ebook_id)
    return render_template('ebook_detail.html', ebook=ebook)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_ebook():
    form = EbookForm()
    if form.validate_on_submit():
        try:
            file = form.ebook_file.data
            filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_ebook = Ebook(
                title=form.title.data,
                description=form.description.data,
                price=form.price.data,
                file_path=filename,
                user_id=current_user.id
            )
            
            db.session.add(new_ebook)
            db.session.commit()
            flash('Ebook cadastrado com sucesso!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro: {str(e)}', 'error')

    return render_template('upload.html', form=form)  # Passe o form para o template

@app.route('/checkout/<int:ebook_id>')
@login_required
def checkout(ebook_id):
    ebook = Ebook.query.get_or_404(ebook_id)
    preference_data = {
        "items": [{
            "title": ebook.title,
            "quantity": 1,
            "unit_price": float(ebook.price),
            "description": ebook.description[:250]
        }],
        "back_urls": {
            "success": url_for('ebook_detail', ebook_id=ebook.id, _external=True),
            "failure": url_for('ebook_detail', ebook_id=ebook.id, _external=True)
        }
    }
    preference = sdk.preference().create(preference_data)
    return redirect(preference["response"]["init_point"])

# Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Email ou senha incorretos', 'error')
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email e senha são obrigatórios', 'error')
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return redirect(url_for('register'))
            
        try:
            new_user = User(
                email=email,
                password=generate_password_hash(password, method='scrypt')
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar conta: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@app.route('/admin/usuarios')
@login_required
@admin_required
def listar_usuarios():
    usuarios = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Comandos CLI
@app.cli.command('init-db')
def init_db():
    """Inicializa o banco de dados"""
    db.create_all()
    
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
    
    print('✅ Banco de dados inicializado!')

@app.cli.command('seed-db')
def seed_db():
    """Popula o banco com dados de teste"""
    fake = Faker()
    
    for _ in range(10):
        ebook = Ebook(
            title=fake.sentence(nb_words=3),
            description=fake.paragraph(nb_sentences=5),
            price=float(fake.random_number(digits=2)),
            file_path=f'sample_{fake.uuid4()}.pdf',
            user_id=1
        )
        db.session.add(ebook)
    
    db.session.commit()
    print('📚 Dados de teste inseridos!')

app = create_app()    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)