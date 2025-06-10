from flask import Flask, request, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from flask_cors import CORS
from tabulate import tabulate  # <-- Adicionado para exibir no terminal

# Carrega variáveis de ambiente do .env
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["https://vagas-rj.onrender.com"])

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Função de conexão
def conectar():
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Erro ao conectar no banco de dados: {e}")
        raise

# Criação da tabela, caso não exista
def criar_tabela_se_nao_existir():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidatos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                data_nascimento TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL,
                cpf TEXT NOT NULL,
                curriculo TEXT NOT NULL
            );
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tabela 'candidatos' verificada/criada.")
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")

# Rota de envio de dados
@app.route('/enviar', methods=['POST'])
def receber_dados():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Dados não recebidos"}), 400

    print("📨 Dados recebidos:", data)

    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO candidatos (nome, data_nascimento, telefone, email, cpf, curriculo)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            data.get('nome'),
            data.get('data_nascimento'),
            data.get('telefone'),
            data.get('email'),
            data.get('cpf'),
            data.get('curriculo')
        ))
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Candidato salvo com sucesso!")
        return jsonify({"message": "Candidatura enviada com sucesso!"}), 200

    except Exception as e:
        print(f"❌ Erro no servidor: {e}")
        return jsonify({"message": f"Erro ao salvar os dados: {str(e)}"}), 500

# 🚀 NOVA ROTA ADICIONADA: /consultar
@app.route('/consultar', methods=['GET'])
def consultar_candidatos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, data_nascimento, telefone, email, cpf, curriculo FROM candidatos;")
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        print("📋 Candidatos cadastrados:")
        print(tabulate(rows, headers=colnames, tablefmt='grid'))

        return jsonify([
            dict(zip(colnames, row)) for row in rows
        ]), 200

    except Exception as e:
        print(f"❌ Erro ao consultar candidatos: {e}")
        return jsonify({"message": f"Erro ao consultar candidatos: {str(e)}"}), 500

criar_tabela_se_nao_existir()

# Inicialização
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
        
