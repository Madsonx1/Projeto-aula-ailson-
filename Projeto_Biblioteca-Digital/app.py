db_path = 'database/base.db'

from flask import Flask, render_template, url_for, request, redirect
import sqlite3
import os
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)

csrf = CSRFProtect(app)

app.secret_key = 'minha_chave_secreta_segura'
app.WTF_CSRF_SECRET_KEY = 'minha_chave_secreta_segura'

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS categoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS livro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            cat_id INT,
            capa BLOB,
            ativo INTEGER,
            FOREIGN KEY(cat_id) REFERENCES categoria(id)
            
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def conexao():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def listarcategoria():
    conn = conexao()
    categoria = conn.execute('SELECT * FROM categoria ORDER BY nome').fetchall()
    conn.close()
    return render_template('listar_categoria.html', categoria=categoria)

@app.route("/nova_categoria", methods=["GET", "POST"])
def novacategoria():
    if request.method == 'POST':
        nome = request.form['nome']
        conn = conexao()
        conn.execute('''
            INSERT INTO categoria (nome)
            VALUES (?)''', (nome,))
        conn.commit()
        conn.close()
        return redirect(url_for('listarcategoria'))


    return render_template('cadastrar_categoria.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editarCategoria(id):
    conn = conexao()
    categoria = conn.execute('SELECT * FROM categoria WHERE id = ?',(id,)).fetchone()
    if not categoria:
        return redirect(url_for('listarcategoria'))
    if request.method == 'POST':
        nome = request.form['nome']
        conn.execute('''
            UPDATE categoria SET nome=? WHERE id=?''',(nome, id))
        conn.commit()
        conn.close()
        return redirect(url_for('listarcategoria'))
    
    conn.close()
    return render_template('editar_categoria.html', categoria=categoria)

@app.route('/excluir_categoria/<int:id>', methods=['POST'])
def excluirCategoria(id):
    conn = conexao()
    conn.execute('DELETE FROM categoria WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('listarcategoria'))

@app.route("/listar_livros")
def listarLivros():
    conn = conexao()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT livro.id, livro.nome, livro.descricao, categoria.nome as categoria
        FROM livro
        LEFT JOIN categoria ON livro.cat_id = categoria.id
        WHERE livro.ativo = 1
    ''')
    livros = cursor.fetchall()
    conn.close()

    return render_template('listar_livros.html', livros=livros)

@app.route("/novo_livro", methods=["GET", "POST"])
def novoLivro():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['cat_id']


    return render_template('cadastrar_livro.html')


if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0')
