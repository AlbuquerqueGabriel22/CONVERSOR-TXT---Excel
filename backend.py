from flask import Flask, redirect, render_template, flash, request, url_for
from pathlib import Path

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/formulario', methods=['GET', 'POST'])
def fomula():
    return render_template('formulario.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cada():
    return render_template('cadastro.html')