import sqlite3

def conectar():
    return sqlite3.connect("igreja.db")

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS perfis (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            perfil_id INTEGER,
            ativo BOOLEAN DEFAULT 1,
            ultimo_login TEXT,
            FOREIGN KEY (perfil_id) REFERENCES perfis(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            categoria_id INTEGER,
            descricao TEXT,
            criado_por INTEGER,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes INTEGER NOT NULL,
            ano INTEGER NOT NULL,
            valor REAL NOT NULL,
            criado_por INTEGER,
            UNIQUE(mes, ano)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            acao TEXT,
            autor_id INTEGER
        )
    """)

    conn.commit()
    conn.close()

def popular_dados_iniciais():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM perfis")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO perfis (nome) VALUES (?)",
            [("Administrador",), ("Pastor",), ("Tesoureiro",), ("Secretária",)]
        )

    conn.commit()
    conn.close()

def criar_usuario_admin():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM usuarios WHERE perfil_id = 1")
    if cur.fetchone()[0] == 0:
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, perfil_id, ativo, ultimo_login)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("Administrador", "admin@igreja.com", "admin", 1, 1, None))
        print("Usuário administrador criado: admin@igreja.com / admin")

    conn.commit()
    conn.close()

def popular_categorias():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM categorias")
    if cur.fetchone()[0] == 0:
        categorias = [
            ("Dízimo", "R"),
            ("Oferta", "R"),
            ("Doação", "R"),
            ("Campanha", "R"),
            ("Energia", "D"),
            ("Água", "D"),
            ("Salário", "D"),
            ("Outros", "D"),
            ("Outros", "R"),
            ("Manutenção", "D")
        ]
        cur.executemany("INSERT INTO categorias (nome, tipo) VALUES (?, ?)", categorias)
        print("Categorias padrão inseridas.")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    criar_tabelas()
    popular_dados_iniciais()
    criar_usuario_admin()
    popular_categorias()
