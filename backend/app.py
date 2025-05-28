from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

# Criação do app
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# -------------------------
# ROTAS DE INTERFACE
# -------------------------

# Página inicial: tela de login
@app.route('/')
def login_page():
    return send_from_directory(app.static_folder, 'index.html')

# Rota para registro visual (se quiser registrar.html também como página)
@app.route('/registrar')
def registrar_page():
    return send_from_directory(app.static_folder, 'registrar.html')

# Rota para outras páginas do frontend (como index.html, projetos.html etc)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# -------------------------
# BANCO DE DADOS
# -------------------------

# Criar tabela de projetos
def init_projetos():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descricao TEXT,
            imagem TEXT,
            link TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Criar tabela de usuários
def init_users():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Inicializa o banco
init_projetos()
init_users()

# -------------------------
# ROTAS DE API (Back-End)
# -------------------------

# LOGIN
@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({'success': True})
    return jsonify({'success': False})

# REGISTRO
@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Usuário já existe'})
    finally:
        conn.close()

# LISTAR PROJETOS
@app.route('/api/projetos', methods=['GET'])
def get_projetos():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM projetos')
    projetos = [
        {'id': row[0], 'titulo': row[1], 'descricao': row[2], 'imagem': row[3], 'link': row[4]}
        for row in c.fetchall()
    ]
    conn.close()
    return jsonify(projetos)

# ADICIONAR PROJETO
@app.route('/api/projetos', methods=['POST'])
def add_projeto():
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO projetos (titulo, descricao, imagem, link) 
        VALUES (?, ?, ?, ?)''',
        (data['titulo'], data['descricao'], data['imagem'], data['link'])
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'Projeto adicionado'}), 201


@app.route('/api/projetos/<int:projeto_id>', methods=['PUT'])
def editar_projeto(projeto_id):
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        UPDATE projetos 
        SET titulo = ?, descricao = ?, imagem = ?, link = ?
        WHERE id = ?
    ''', (data['titulo'], data['descricao'], data['imagem'], data['link'], projeto_id))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Projeto atualizado'})




#remover projeto
@app.route('/api/projetos/<int:projeto_id>', methods=['DELETE'])
def delete_projeto(projeto_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM projetos WHERE id = ?', (projeto_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'Projeto removido'})


# -------------------------
# RODAR SERVIDOR
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
