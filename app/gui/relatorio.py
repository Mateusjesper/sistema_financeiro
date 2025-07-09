import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from app.banco import conectar
import matplotlib.pyplot as plt
from PIL import Image

def tela_relatorio():
    win = tk.Toplevel(); win.title("Relatórios"); win.geometry("700x500")
    tk.Label(win,text="Relatório de Lançamentos",font=("Arial",14)).pack(pady=10)

    frm = tk.Frame(win); frm.pack()
    tk.Label(frm,text="Ano:").grid(row=0,column=0)
    ano = tk.Entry(frm,width=6); ano.insert(0,datetime.now().year); ano.grid(row=0,column=1)
    tk.Label(frm,text="Mês (1-12):").grid(row=0,column=2)
    mes = tk.Entry(frm,width=4); mes.insert(0,datetime.now().month); mes.grid(row=0,column=3)

    def buscar():
        for i in tree.get_children(): tree.delete(i)
        cur = conectar().cursor()
        cur.execute("""
            SELECT l.data, l.valor, l.tipo, c.nome, l.descricao
            FROM lancamentos l JOIN categorias c ON l.categoria_id = c.id
            WHERE strftime('%Y', l.data) = ? AND strftime('%m', l.data) = ?
            ORDER BY l.data
        """, (ano.get(), f"{int(mes.get()):02}"))
        for r in cur.fetchall():
            tipo = "Receita" if r[2]=="R" else "Despesa"
            tree.insert("", "end", values=(r[0], f"R$ {r[1]:.2f}".replace(".",","), tipo, r[3], r[4]))

    tk.Button(win,text="Buscar",command=buscar).pack(pady=5)
    tree = ttk.Treeview(win, columns=("Data","Valor","Tipo","Categoria","Descrição"), show="headings")
    for col in tree["columns"]: tree.heading(col,text=col)
    tree.pack(fill="both",expand=True)

    def exportar_excel():
        if not tree.get_children(): return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        wb = Workbook(); ws = wb.active
        ws.append(tree["columns"])
        for row in tree.get_children():
            ws.append(tree.item(row)["values"])
        wb.save(path); messagebox.showinfo("OK","Salvo em Excel.")

    def exportar_pdf():
        if not tree.get_children(): return

        path = filedialog.asksaveasfilename(defaultextension=".pdf")

        cur = conectar().cursor()
        cur.execute("""
            SELECT c.nome,
                   IFNULL(SUM(CASE WHEN l.tipo='R' THEN l.valor END), 0),
                   IFNULL(SUM(CASE WHEN o.valor IS NOT NULL THEN o.valor ELSE 0 END), 0)
            FROM categorias c
            LEFT JOIN lancamentos l ON l.categoria_id = c.id
            LEFT JOIN orcamentos o ON o.categoria_id = c.id AND strftime('%Y-%m', o.mes) = ?
            WHERE c.tipo IN ('R', 'D')
            GROUP BY c.id
        """, (f"{datetime.now().year}-{datetime.now().month:02}",))
        dados = cur.fetchall()

        categorias = [row[0] for row in dados]
        realizado = [row[1] for row in dados]
        orcado = [row[2] for row in dados]

        plt.figure(figsize=(8, 4))
        x = range(len(categorias))
        plt.bar(x, orcado, width=0.4, label='Orçado', align='center')
        plt.bar(x, realizado, width=0.4, label='Realizado', align='edge')
        plt.xticks(x, categorias, rotation=45, ha='right')
        plt.ylabel('Valor (R$)')
        plt.title('Orçado vs Realizado por Categoria')
        plt.legend()
        plt.tight_layout()
        plt.savefig("grafico_orcado.png")
        plt.close()

        c = canvas.Canvas(path, pagesize=A4)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 800, "Relatório de Lançamentos")
        y = 770
        c.setFont("Helvetica", 10)

        for row in tree.get_children():
            dados_linha = tree.item(row)["values"]
            linha = f"{dados_linha[0]} | {dados_linha[1]} | {dados_linha[2]} | {dados_linha[3]} | {dados_linha[4]}"
            c.drawString(50, y, linha)
            y -= 15
            if y < 200:
                break

        c.drawImage("grafico_orcado.png", 50, 100, width=500, height=200)
        c.save()

        messagebox.showinfo("OK", "PDF com gráfico gerado com sucesso.")

    exp = tk.Frame(win); exp.pack(pady=10)
    tk.Button(exp,text="Exportar Excel",command=exportar_excel,bg="#0dcaf0").pack(side="left",padx=10)
    tk.Button(exp,text="Exportar PDF",command=exportar_pdf,bg="#6f42c1",fg="white").pack(side="left",padx=10)
