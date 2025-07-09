from app.banco import conectar
from datetime import datetime


def criar_tabela_historico():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            acao TEXT,
            autor_id INTEGER,
            FOREIGN KEY (autor_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()


def registrar_acao(acao: str, autor_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historico (acao, autor_id)
        VALUES (?, ?)
    """, (acao, autor_id))
    conn.commit()
    conn.close()


def listar_historico():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.data_hora, h.acao, u.nome
        FROM historico h
        JOIN usuarios u ON h.autor_id = u.id
        ORDER BY h.data_hora DESC
    """)
    dados = cur.fetchall()
    conn.close()
    return dados
