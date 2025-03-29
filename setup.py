import subprocess

def setup_project():
    # Criar ambiente virtual
    subprocess.run(["python", "-m", "venv", "venv"])
    
    # Instalar dependências
    requirements = [
        "flask",
        "flask-sqlalchemy",
        "psycopg2-binary",
        "python-dotenv",
        "flask-login",
        "mercadopago"
    ]
    subprocess.run(["pip", "install"] + requirements)

if __name__ == "__main__":
    setup_project()