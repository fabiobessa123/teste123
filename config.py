import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'uma-chave-muito-secreta')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://usuario:senha@localhost/meubanco')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'epub'}