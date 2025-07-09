import tkinter as tk
from tkinter import messagebox
from app.banco import conectar
from datetime import datetime

usuario_logado = {}

def iniciar_login():
    def entrar():
        from app.gui.dashboard import abrir_dashboard  # 🔁 Importação movida para dentro da função

        email_input = email.get()
        senha_input = senha.get()

        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, perfil_id, ultimo_login FROM usuarios
            WHERE email = ? AND senha_hash = ?
        """, (email_input, senha_input))
        resultado = cur.fetchone()

        if resultado:
            usuario = {
                "id": resultado[0],
                "nome": resultado[1],
                "perfil_id": resultado[2],
                "ultimo_login": resultado[3]
            }
            root.destroy()
            abrir_dashboard(usuario)
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    root = tk.Tk()
    root.title("Login")
    tk.Label(root, text="Email").pack()
    email = tk.Entry(root)
    email.pack()
    tk.Label(root, text="Senha").pack()
    senha = tk.Entry(root, show="*")
    senha.pack()
    tk.Button(root, text="Entrar", command=entrar).pack(pady=10)
    root.mainloop()
