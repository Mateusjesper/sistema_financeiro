import tkinter as tk, tkinter.ttk as ttk
from tkinter import messagebox
from datetime import date
from app.banco import conectar

def tela_receitas():
    win = tk.Toplevel(); win.title("Receitas"); win.geometry("500x380")
    tk.Label(win,text="Lançar Receita",font=("Arial",14)).pack(pady=8)
    frm = tk.Frame(win); frm.pack(pady=6)

    tk.Label(frm,text="Data:").grid(row=0,column=0,sticky="e")
    dt = tk.Entry(frm); dt.insert(0,date.today().strftime("%Y-%m-%d")); dt.grid(row=0,column=1)

    tk.Label(frm,text="Valor (R$):").grid(row=1,column=0,sticky="e")
    val = tk.Entry(frm); val.grid(row=1,column=1)

    tk.Label(frm,text="Categoria:").grid(row=2,column=0,sticky="e")
    cat = ttk.Combobox(frm,state="readonly"); cat.grid(row=2,column=1)

    tk.Label(frm,text="Descrição:").grid(row=3,column=0,sticky="e")
    desc = tk.Entry(frm); desc.grid(row=3,column=1)

    cur = conectar().cursor(); cur.execute("SELECT id,nome FROM categorias WHERE tipo='R'")
    mapa = {nome:str(cid) for cid,nome in cur.fetchall()}
    cat["values"] = list(mapa.keys())

    def salvar():
        try:
            valor = float(val.get().replace(",","."))
            cat_id = mapa.get(cat.get())
            if not cat_id: raise ValueError("Categoria inválida")
            con = conectar(); c = con.cursor()
            c.execute("""INSERT INTO lancamentos(data,valor,tipo,categoria_id,descricao,criado_por)
                         VALUES (?,?,?,?,?,1)""",(dt.get(),valor,'R',cat_id,desc.get()))
            con.commit(); con.close()
            messagebox.showinfo("OK","Receita salva."); win.destroy()
        except Exception as e:
            messagebox.showerror("Erro",str(e))

    tk.Button(win,text="Salvar Receita",command=salvar,bg="#198754",fg="white").pack(pady=10)