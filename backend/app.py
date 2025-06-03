from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

# ---------------------
# CLASSES E MÉTODOS
# ---------------------

class BancoDeDados:
    DB_NAME = 'database.db'

    @classmethod
    def conectar(cls):
        return sqlite3.connect(cls.DB_NAME)

    @classmethod
    def criar_tabelas(cls):
        with cls.conectar() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS projetos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT, descricao TEXT, imagem TEXT, link TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE, password TEXT
                )
            ''')
            conn.commit()

class UsuarioController:
    def login(self, username, password):
        conn = BancoDeDados.conectar()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()
        return jsonify({'success': bool(user)})

    def registrar(self, username, password):
        conn = BancoDeDados.conectar()
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return jsonify({'success': True})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': 'Usuário já existe'})
        finally:
            conn.close()

class ProjetoController:
    def listar(self):
        conn = BancoDeDados.conectar()
        c = conn.cursor()
        c.execute('SELECT * FROM projetos')
        projetos = [
            {'id': row[0], 'titulo': row[1], 'descricao': row[2], 'imagem': row[3], 'link': row[4]}
            for row in c.fetchall()
        ]
        conn.close()
        return jsonify(projetos)

    def criar(self, data):
        conn = BancoDeDados.conectar()
        c = conn.cursor()
        c.execute('''
            INSERT INTO projetos (titulo, descricao, imagem, link)
            VALUES (?, ?, ?, ?)''',
            (data['titulo'], data['descricao'], data['imagem'], data['link']))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Projeto adicionado'}), 201

    def editar(self, projeto_id, data):
        conn = BancoDeDados.conectar()
        c = conn.cursor()
        c.execute('''
            UPDATE projetos
            SET titulo = ?, descricao = ?, imagem = ?, link = ?
            WHERE id = ?''',
            (data['titulo'], data['descricao'], data['imagem'], data['link'], projeto_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Projeto atualizado'})

    def remover(self, projeto_id):
        conn = BancoDeDados.conectar()
        c = conn.cursor()
        c.execute('DELETE FROM projetos WHERE id = ?', (projeto_id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'Projeto removido'})

# ---------------------
# FLASK APP
# ---------------------

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

# Instanciar os controladores
usuario_ctrl = UsuarioController()
projeto_ctrl = ProjetoController()

# Inicializar banco
BancoDeDados.criar_tabelas()

# ---------------------
# ROTAS DE INTERFACE
# ---------------------

@app.route('/')
def login_page():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/registrar')
def registrar_page():
    return send_from_directory(app.static_folder, 'registrar.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# ---------------------
# ROTAS DE API
# ---------------------

@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    return usuario_ctrl.login(data['username'], data['password'])

@app.route('/api/register', methods=['POST'])
def register_api():
    data = request.get_json()
    return usuario_ctrl.registrar(data['username'], data['password'])

@app.route('/api/projetos', methods=['GET'])
def get_projetos():
    return projeto_ctrl.listar()

@app.route('/api/projetos', methods=['POST'])
def add_projeto():
    data = request.get_json()
    return projeto_ctrl.criar(data)

@app.route('/api/projetos/<int:projeto_id>', methods=['PUT'])
def editar_projeto(projeto_id):
    data = request.get_json()
    return projeto_ctrl.editar(projeto_id, data)

@app.route('/api/projetos/<int:projeto_id>', methods=['DELETE'])
def delete_projeto(projeto_id):
    return projeto_ctrl.remover(projeto_id)

# ---------------------
# INICIAR SERVIDOR
# ---------------------

if __name__ == '__main__':
    app.run(debug=True)
