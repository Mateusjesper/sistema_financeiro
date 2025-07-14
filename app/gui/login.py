import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from app.banco import conectar
from app.gui.dashboard import abrir_dashboard
from datetime import datetime

usuario_logado = {}

def iniciar_login():
    login_win = tk.Tk()
    login_win.title("Login")
    login_win.geometry("400x400")
    login_win.configure(bg="#f4f4f4")

    def entrar():
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
            usuario_logado["id"] = resultado[0]
            usuario_logado["nome"] = resultado[1]
            usuario_logado["perfil_id"] = resultado[2]
            usuario_logado["ultimo_login"] = resultado[3]

            cur.execute("UPDATE usuarios SET ultimo_login = ? WHERE id = ?", (datetime.now(), resultado[0]))
            conn.commit()
            conn.close()

            login_win.destroy()
            abrir_dashboard(usuario_logado)
        else:
            messagebox.showerror("Erro", "Email ou senha inválidos.")
            conn.close()

    def recuperar_senha():
        messagebox.showinfo("Recuperar Senha", "Por favor, entre em contato com o administrador para redefinir a senha.")

    #Logo
    try:
        img_path = "app/gui/imagens/logo.png"
        img = Image.open(img_path)
        img = img.resize((100, 100))
        img_tk = ImageTk.PhotoImage(img)
        logo_label = tk.Label(login_win, image=img_tk, bg="#f4f4f4")
        logo_label.image = img_tk
        logo_label.pack(pady=(20, 5))

    except Exception as e:
        print(f"Erro ao carregar a logo: {e}")

    # Formulário
    form_frame = tk.Frame(login_win, bg="#f4f4f4")
    form_frame.pack(pady=30)

    tk.Label(form_frame, text="Email:", bg="#f4f4f4", font=("Arial", 12)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    email = tk.Entry(form_frame, width=30)
    email.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(form_frame, text="Senha:", bg="#f4f4f4", font=("Arial", 12)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    senha = tk.Entry(form_frame, show="*", width=30)
    senha.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(login_win, text="Entrar", command=entrar, bg="#4682B4", fg="white", font=("Arial", 11), width=15).pack(pady=10)
    tk.Button(login_win, text="Esqueci minha senha", command=recuperar_senha, bg="#f4f4f4", fg="blue", bd=0).pack()

    login_win.mainloop()