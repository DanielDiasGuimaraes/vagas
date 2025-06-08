from flask import Flask, request, jsonify
import psycopg2
import os
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def conectar():
    return psycopg2.connect(**DB_CONFIG)

def criar_tabela_se_nao_existir():
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

@app.route('/enviar', methods=['POST'])
def receber_dados():
    data = request.get_json()

    if not data:
        return jsonify({"message": "Dados não recebidos"}), 400

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
        return jsonify({"message": "Candidatura enviada com sucesso!"}), 200

    except Exception as e:
        return jsonify({"message": f"Erro ao salvar os dados: {e}"}), 500

if __name__ == '__main__':
    criar_tabela_se_nao_existir()
    app.run(debug=True)
