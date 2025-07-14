import tkinter as tk
from tkinter import ttk, messagebox
from app.banco import conectar

def tela_usuarios():
    win = tk.Toplevel()
    win.title("Gerenciar Usuários")
    win.geometry("700x400")

    tree = ttk.Treeview(win, columns=("ID", "Nome", "Email", "Perfil", "Ativo"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    def carregar():
        tree.delete(*tree.get_children())
        cur = conectar().cursor()
        cur.execute("""
            SELECT u.id, u.nome, u.email, p.nome, u.ativo
            FROM usuarios u LEFT JOIN perfis p ON u.perfil_id = p.id
        """)
        for row in cur.fetchall():
            ativo = "Sim" if row[4] else "Não"
            tree.insert("", "end", values=(row[0], row[1], row[2], row[3], ativo))

    def editar_usuario():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção", "Selecione um usuário.")
            return
        dados = tree.item(selecionado[0])["values"]
        editar(dados)

    def editar(dados=None):
        eid = dados[0] if dados else None
        nome_antigo = dados[1] if dados else ""
        email_antigo = dados[2] if dados else ""
        perfil_antigo = dados[3] if dados else ""
        ativo_status = dados[4] if dados else "Sim"

        ed = tk.Toplevel()
        ed.title("Editar Usuário" if dados else "Cadastrar Usuário")

        tk.Label(ed, text="Nome").grid(row=0, column=0)
        nome = tk.Entry(ed); nome.insert(0, nome_antigo); nome.grid(row=0, column=1)

        tk.Label(ed, text="Email").grid(row=1, column=0)
        email = tk.Entry(ed); email.insert(0, email_antigo); email.grid(row=1, column=1)

        tk.Label(ed, text="Senha (nova)").grid(row=2, column=0)
        senha = tk.Entry(ed); senha.grid(row=2, column=1)

        tk.Label(ed, text="Perfil").grid(row=3, column=0)
        perfil_cb = ttk.Combobox(ed, state="readonly")
        cur = conectar().cursor()
        cur.execute("SELECT id, nome FROM perfis")
        perfis = cur.fetchall()
        perfil_map = {nome: pid for pid, nome in perfis}
        perfil_cb["values"] = list(perfil_map.keys())
        perfil_cb.set(perfil_antigo if dados else "")
        perfil_cb.grid(row=3, column=1)

        ativo_var = tk.BooleanVar(value=(ativo_status == "Sim"))
        tk.Checkbutton(ed, text="Ativo", variable=ativo_var).grid(row=4, column=1)

        def salvar_edicao():
            conn = conectar(); cur = conn.cursor()
            pid = perfil_map[perfil_cb.get()]

            # Verifica duplicidade de email ao cadastrar ou editar
            cur.execute("SELECT id FROM usuarios WHERE email = ?", (email.get(),))
            existente = cur.fetchone()
            if existente and (eid is None or existente[0] != eid):
                messagebox.showerror("Erro", "Este email já está em uso.")
                conn.close()
                return

            if eid:  # edição
                if senha.get():
                    cur.execute("""
                        UPDATE usuarios SET nome=?, email=?, senha_hash=?, perfil_id=?, ativo=?
                        WHERE id=?
                    """, (nome.get(), email.get(), senha.get(), pid, ativo_var.get(), eid))
                else:
                    cur.execute("""
                        UPDATE usuarios SET nome=?, email=?, perfil_id=?, ativo=?
                        WHERE id=?
                    """, (nome.get(), email.get(), pid, ativo_var.get(), eid))
            else:  # novo cadastro
                if not senha.get():
                    messagebox.showwarning("Aviso", "Digite uma senha para o novo usuário.")
                    conn.close()
                    return
                cur.execute("""
                    INSERT INTO usuarios (nome, email, senha_hash, perfil_id, ativo)
                    VALUES (?, ?, ?, ?, ?)
                """, (nome.get(), email.get(), senha.get(), pid, ativo_var.get()))

            conn.commit(); conn.close()
            ed.destroy(); carregar()

        tk.Button(ed, text="Salvar", command=salvar_edicao, bg="#0d6efd", fg="white").grid(row=5, column=1, pady=10)

    #Botões
    tk.Button(win, text="Cadastrar Novo", command=lambda: editar(), bg="#198754", fg="white").pack(pady=5)
    tk.Button(win, text="Editar Selecionado", command=editar_usuario, bg="#ffc107").pack(pady=5)
    carregar()
