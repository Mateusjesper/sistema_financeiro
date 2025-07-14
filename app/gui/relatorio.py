import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from app.banco import conectar
import matplotlib.pyplot as plt


def tela_relatorio():
    win = tk.Toplevel()
    win.title("Relatórios")
    win.geometry("700x500")
    tk.Label(win, text="Relatório de Lançamentos", font=("Arial", 14)).pack(pady=10)

    frm = tk.Frame(win)
    frm.pack()
    tk.Label(frm, text="Ano:").grid(row=0, column=0)
    ano = tk.Entry(frm, width=6)
    ano.insert(0, datetime.now().year)
    ano.grid(row=0, column=1)

    tk.Label(frm, text="Mês (1-12):").grid(row=0, column=2)
    mes = tk.Entry(frm, width=4)
    mes.insert(0, datetime.now().month)
    mes.grid(row=0, column=3)

    tree = ttk.Treeview(win, columns=("Data", "Valor", "Tipo", "Categoria", "Descrição"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)

    def buscar():
        for i in tree.get_children():
            tree.delete(i)
        cur = conectar().cursor()
        cur.execute("""
            SELECT l.data, l.valor, l.tipo, c.nome, l.descricao
            FROM lancamentos l JOIN categorias c ON l.categoria_id = c.id
            WHERE strftime('%Y', l.data) = ? AND strftime('%m', l.data) = ?
            ORDER BY l.data
        """, (ano.get(), f"{int(mes.get()):02}"))
        for r in cur.fetchall():
            tipo = "Receita" if r[2] == "R" else "Despesa"
            tree.insert("", "end", values=(r[0], f"R$ {r[1]:.2f}".replace(".", ","), tipo, r[3], r[4]))

    def exportar_excel():
        if not tree.get_children():
            return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not path:
            return
        wb = Workbook()
        ws = wb.active
        ws.append(tree["columns"])
        for row in tree.get_children():
            ws.append(tree.item(row)["values"])
        wb.save(path)
        messagebox.showinfo("Excel Exportado", "Relatório salvo em Excel com sucesso.")

    def exportar_pdf():
        if not tree.get_children():
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if not path:
            return

        receitas = sum(float(tree.item(i)["values"][1].replace("R$ ", "").replace(",", "."))
                       for i in tree.get_children() if tree.item(i)["values"][2] == "Receita")
        despesas = sum(float(tree.item(i)["values"][1].replace("R$ ", "").replace(",", "."))
                       for i in tree.get_children() if tree.item(i)["values"][2] == "Despesa")

        categorias = ["Receitas", "Despesas"]
        valores = [receitas, despesas]

        plt.figure(figsize=(6, 3))
        plt.bar(categorias, valores, color=["green", "red"])
        plt.title("Resumo do Mês")
        plt.ylabel("R$ (Valor)")
        plt.tight_layout()
        plt.savefig("grafico_relatorio.png")
        plt.close()

        c = canvas.Canvas(path, pagesize=A4)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 800, "Relatório de Lançamentos")

        y = 770
        c.setFont("Helvetica", 10)
        for row in tree.get_children():
            dados = tree.item(row)["values"]
            linha = f"{dados[0]} | {dados[1]} | {dados[2]} | {dados[3]} | {dados[4]}"
            c.drawString(50, y, linha)
            y -= 15
            if y < 200:
                break

        c.drawImage("grafico_relatorio.png", 50, 100, width=500, height=200)
        c.save()
        messagebox.showinfo("PDF Exportado", "Relatório em PDF gerado com sucesso.")

    tk.Button(win, text="Buscar", command=buscar).pack(pady=5)

    exp = tk.Frame(win)
    exp.pack(pady=10)

    #Botões
    tk.Button(exp, text="Exportar Excel", command=exportar_excel, bg="#0dcaf0").pack(side="left", padx=10)
    tk.Button(exp, text="Exportar PDF", command=exportar_pdf, bg="#6f42c1", fg="white").pack(side="left", padx=10)
