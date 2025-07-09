import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.banco import conectar

def tela_despesas():
    janela = tk.Toplevel()
    janela.title("Despesas")
    janela.geometry("500x380")

    tk.Label(janela, text="Lançar Despesa", font=("Arial", 14)).pack(pady=8)
    frame = tk.Frame(janela)
    frame.pack(pady=6)

    tk.Label(frame, text="Data:").grid(row=0, column=0, sticky="e")
    entry_data = tk.Entry(frame)
    entry_data.insert(0, date.today().strftime("%Y-%m-%d"))
    entry_data.grid(row=0, column=1)

    tk.Label(frame, text="Valor (R$):").grid(row=1, column=0, sticky="e")
    entry_valor = tk.Entry(frame)
    entry_valor.grid(row=1, column=1)

    tk.Label(frame, text="Categoria:").grid(row=2, column=0, sticky="e")
    combo_categoria = ttk.Combobox(frame, state="readonly")
    combo_categoria.grid(row=2, column=1)

    tk.Label(frame, text="Descrição:").grid(row=3, column=0, sticky="e")
    entry_desc = tk.Entry(frame)
    entry_desc.grid(row=3, column=1)

    cur = conectar().cursor()
    cur.execute("SELECT id, nome FROM categorias WHERE tipo = 'D'")
    mapa = {nome: str(cid) for cid, nome in cur.fetchall()}
    combo_categoria["values"] = list(mapa.keys())

    def salvar():
        try:
            valor = float(entry_valor.get().replace(",", "."))
            cat_id = mapa.get(combo_categoria.get())
            if not cat_id:
                raise ValueError("Categoria inválida")
            con = conectar()
            cur = con.cursor()
            cur.execute("""
                INSERT INTO lancamentos (data, valor, tipo, categoria_id, descricao, criado_por)
                VALUES (?, ?, 'D', ?, ?, 1)
            """, (entry_data.get(), valor, cat_id, entry_desc.get()))
            con.commit(); con.close()
            messagebox.showinfo("Sucesso", "Despesa registrada com sucesso.")
            janela.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(janela, text="Salvar Despesa", command=salvar, bg="#dc3545", fg="white").pack(pady=10)