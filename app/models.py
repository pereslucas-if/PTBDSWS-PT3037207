import os
import json
import sqlite3
from datetime import datetime


BASEDIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)

USERS_FILE = os.path.join(BASEDIR, 'usuarios.json')
DATABASE_FILE = os.path.join(BASEDIR, 'emails.db')


def inicializar_banco():
    conexao = sqlite3.connect(DATABASE_FILE)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            de TEXT NOT NULL,
            para TEXT NOT NULL,
            assunto TEXT NOT NULL,
            texto TEXT NOT NULL,
            data_hora TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()


def salvar_email(de, destinatarios, assunto, texto):
    conexao = sqlite3.connect(DATABASE_FILE)
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO emails
        (de, para, assunto, texto, data_hora)
        VALUES (?, ?, ?, ?, ?)
    """, (
        de,
        '\n'.join(destinatarios),
        assunto,
        texto,
        datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    ))

    conexao.commit()
    conexao.close()


def carregar_emails():
    conexao = sqlite3.connect(DATABASE_FILE)
    conexao.row_factory = sqlite3.Row

    cursor = conexao.cursor()
    cursor.execute("""
        SELECT *
        FROM emails
        ORDER BY id DESC
    """)

    emails = cursor.fetchall()
    conexao.close()

    return emails


def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
        usuarios = [
            {
                "nome": "john",
                "funcao": "Administrator"
            }
        ]

        salvar_usuarios(usuarios)
        return usuarios

    with open(USERS_FILE, 'r', encoding='utf-8') as arquivo:
        return json.load(arquivo)


def salvar_usuarios(usuarios):
    with open(USERS_FILE, 'w', encoding='utf-8') as arquivo:
        json.dump(
            usuarios,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def adicionar_usuario(nome):
    usuarios = carregar_usuarios()

    for usuario in usuarios:
        if usuario['nome'].lower() == nome.lower():
            return False

    usuarios.append({
        "nome": nome,
        "funcao": "User"
    })

    salvar_usuarios(usuarios)

    return True