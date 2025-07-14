import tkinter as tk
from tkinter import ttk, messagebox
from app.banco import conectar

def gerenciar_lancamentos(usuario_id):
    win = tk.Toplevel()
    win.title("Gerenciar Lançamentos")
    win.geometry("750x450")

    # Filtro
    filtro_frame = tk.Frame(win)
    filtro_frame.pack(pady=10)

    tk.Label(filtro_frame, text="Tipo:").grid(row=0, column=0, padx=5)
    tipo_cb = ttk.Combobox(filtro_frame, state="readonly", values=["Receita", "Despesa"])
    tipo_cb.set("Receita")
    tipo_cb.grid(row=0, column=1, padx=5)

    # Tabela
    colunas = ("ID", "Data", "Valor", "Categoria", "Descrição")
    tree = ttk.Treeview(win, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Funções
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
        if messagebox.askyesno("Confirmação", "Deseja realmente excluir este lançamento?"):
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
        edit_win.geometry("300x320")

        tk.Label(edit_win, text="Data:").pack(pady=2)
        data_entry = tk.Entry(edit_win)
        data_entry.insert(0, data_antiga)
        data_entry.pack()

        tk.Label(edit_win, text="Valor (R$):").pack(pady=2)
        valor_entry = tk.Entry(edit_win)
        valor_entry.insert(0, str(valor_antigo))
        valor_entry.pack()

        #Categoria
        tk.Label(edit_win, text="Categoria:").pack(pady=2)
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

        tk.Label(edit_win, text="Descrição:").pack(pady=2)
        desc_entry = tk.Entry(edit_win)
        desc_entry.insert(0, descricao_antiga)
        desc_entry.pack()

        def salvar():
            try:
                nova_data = data_entry.get()
                novo_valor = float(valor_entry.get().replace(",", "."))
                nova_desc = desc_entry.get()
                nova_categoria = cat_map.get(cat_cb.get())

                conn2 = conectar()
                cur2 = conn2.cursor()
                cur2.execute("""
                    UPDATE lancamentos
                    SET data=?, valor=?, categoria_id=?, descricao=?
                    WHERE id=?
                """, (nova_data, novo_valor, nova_categoria, nova_desc, eid))
                conn2.commit()
                conn2.close()
                edit_win.destroy()
                carregar()
            except Exception as e:
                messagebox.showerror("Erro ao salvar", str(e))

        tk.Button(edit_win, text="Salvar", command=salvar, bg="#0d6efd", fg="white").pack(pady=10)

    # Botões
    botoes_frame = tk.Frame(win)
    botoes_frame.pack(pady=10)

    tk.Button(botoes_frame, text="Carregar", command=carregar, bg="#198754", fg="white", width=10).grid(row=0, column=0, padx=5)
    tk.Button(botoes_frame, text="Editar", command=editar, bg="#ffc107", width=10).grid(row=0, column=1, padx=5)
    tk.Button(botoes_frame, text="Excluir", command=excluir, bg="#dc3545", fg="white", width=10).grid(row=0, column=2, padx=5)

    carregar()
