from flask import Flask, redirect, render_template, flash, request, url_for, send_from_directory
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import openpyxl
import os
import json

app = Flask(__name__)
app.secret_key = 'Eren@8511'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index'
login_manager.login_message = "Por favor, faça login para acessar esta página."
login_manager.login_message_category = "info"

UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

USERS_FILE = 'users.json'

def load_users():
    if not os.path.exists(USERS_FILE) or os.path.getsize(USERS_FILE) == 0:
        return {}
    with open(USERS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {} # Retorna um dicionário vazio se o arquivo estiver corrompido/malformado

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        return User(user_id)
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        users = load_users()

        if email in users and check_password_hash(users[email]['password'], password):
            user = User(email)
            login_user(user)
            return redirect(url_for('fomula'))
        else:
            flash('Email ou senha inválidos.', 'error')
            return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
@login_required
def fomula():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado')
            return redirect(request.url)
        if file and file.filename.endswith('.txt'):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                with open(filepath, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                    if not linhas:
                        flash('Erro: O arquivo enviado está vazio.')
                        return redirect(request.url)

                    cabecalhos = [campo.split(':')[0] for campo in linhas[0].strip().split('|')]
                    sheet.append(cabecalhos)

                    for linha in linhas:
                        if not linha.strip():
                            continue
                        
                        campos = linha.strip().split('|')
                        valores = []
                        for campo in campos:
                            partes = campo.split(':', 1) 
                            valores.append(partes[1] if len(partes) > 1 else "") 
                        sheet.append(valores)
                
                excel_filename = f"{Path(filename).stem}.xlsx"
                excel_filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], excel_filename)
                workbook.save(excel_filepath)
                return send_from_directory(app.config['DOWNLOAD_FOLDER'], excel_filename, as_attachment=True)
            except Exception as e:
                flash(f'Erro ao processar o arquivo: {e}')
                return redirect(request.url)

    return render_template('formulario.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cada():
    if request.method == 'POST':
        name = request.form.get('nome')
        email = request.form.get('email')
        password = request.form.get('senha')
        password_confirm = request.form.get('senha_confirma')

        if password != password_confirm:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('cada'))

        users = load_users()
        if email in users:
            flash('Este email já está cadastrado.', 'error')
            return redirect(url_for('cada'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users[email] = {'name': name, 'password': hashed_password}
        save_users(users)

        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('index'))

    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))