import tkinter as tk
from tkinter import ttk, messagebox
from app.banco import conectar

def gerenciar_lancamentos(usuario_id):
    win = tk.Toplevel()
    win.title("Gerenciar Lançamentos")
    win.geometry("700x400")

    filtro_frame = tk.Frame(win)
    filtro_frame.pack(pady=10)

    tk.Label(filtro_frame, text="Tipo:").grid(row=0, column=0)
    tipo_cb = ttk.Combobox(filtro_frame, state="readonly", values=["Receita", "Despesa"])
    tipo_cb.set("Receita")
    tipo_cb.grid(row=0, column=1, padx=10)

    tree = ttk.Treeview(win, columns=("ID", "Data", "Valor", "Categoria", "Descrição"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True, pady=10)

    def carregar():
        tipo = "R" if tipo_cb.get() == "Receita" else "D"
        tree.delete(*tree.get_children())
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT l.id, l.data, l.valor, c.nome, l.descricao
            FROM lancamentos l
            JOIN categorias c ON c.id = l.categoria_id
            WHERE l.tipo = ?
            ORDER BY l.data DESC
        """, (tipo,))
        for row in cur.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def editar():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um lançamento para editar.")
            return
        dados = tree.item(selecionado[0])["values"]
        abrir_edicao(dados)

    def excluir():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um lançamento para excluir.")
            return
        dados = tree.item(selecionado[0])["values"]
        resposta = messagebox.askyesno("Confirmação", "Deseja excluir este lançamento?")
        if resposta:
            conn = conectar()
            cur = conn.cursor()
            cur.execute("DELETE FROM lancamentos WHERE id = ?", (dados[0],))
            conn.commit()
            conn.close()
            carregar()

    def abrir_edicao(dados):
        eid, data_antiga, valor_antigo, categoria_antiga, descricao_antiga = dados

        edit_win = tk.Toplevel()
        edit_win.title("Editar Lançamento")
        edit_win.geometry("300x300")

        tk.Label(edit_win, text="Data:").pack()
        data_entry = tk.Entry(edit_win)
        data_entry.insert(0, data_antiga)
        data_entry.pack()

        tk.Label(edit_win, text="Valor (R$):").pack()
        valor_entry = tk.Entry(edit_win)
        valor_entry.insert(0, str(valor_antigo))
        valor_entry.pack()

        tk.Label(edit_win, text="Descrição:").pack()
        desc_entry = tk.Entry(edit_win)
        desc_entry.insert(0, descricao_antiga)
        desc_entry.pack()

        tk.Label(edit_win, text="Categoria:").pack()
        cat_cb = ttk.Combobox(edit_win, state="readonly")
        conn = conectar()
        cur = conn.cursor()
        tipo = "R" if tipo_cb.get() == "Receita" else "D"
        cur.execute("SELECT id, nome FROM categorias WHERE tipo = ?", (tipo,))
        categorias = cur.fetchall()
        cat_map = {nome: cid for cid, nome in categorias}
        cat_cb["values"] = list(cat_map.keys())
        cat_cb.set(categoria_antiga)
        cat_cb.pack()

        def salvar():
            try:
                nova_data = data_entry.get()
                novo_valor = float(valor_entry.get().replace(",", "."))
                nova_desc = desc_entry.get()
                cat_id = cat_map.get(cat_cb.get())

                conn2 = conectar()
                cur2 = conn2.cursor()
                cur2.execute("""
                    UPDATE lancamentos
                    SET data=?, valor=?, categoria_id=?, descricao=?
                    WHERE id=?
                """, (nova_data, novo_valor, cat_id, nova_desc, eid))
                conn2.commit()
                conn2.close()
                edit_win.destroy()
                carregar()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

        tk.Button(edit_win, text="Salvar", command=salvar, bg="#0d6efd", fg="white").pack(pady=10)

    tk.Button(win, text="Carregar", command=carregar).pack()
    tk.Button(win, text="Editar", command=editar, bg="#ffc107").pack(pady=5)
    tk.Button(win, text="Excluir", command=excluir, bg="#dc3545", fg="white").pack(pady=5)

    carregar()
