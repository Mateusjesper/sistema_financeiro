import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from app.banco import conectar

def tela_graficos():
    win = tk.Toplevel(); win.title("Gráficos"); win.geometry("1000x500")
    top = tk.Label(win,text="Gráficos de Tendência e Distribuição",font=("Arial",14)); top.pack(pady=10)

    frm = tk.Frame(win); frm.pack(fill="both",expand=True)
    esq = tk.Frame(frm); esq.pack(side="left",fill="both",expand=True)
    dir = tk.Frame(frm); dir.pack(side="left",fill="both",expand=True)

    cur = conectar().cursor()
    cur.execute("""
        SELECT strftime('%Y-%m', data),
               SUM(CASE WHEN tipo='R' THEN valor ELSE 0 END),
               SUM(CASE WHEN tipo='D' THEN valor ELSE 0 END)
        FROM lancamentos GROUP BY 1 ORDER BY 1
    """)
    dados = cur.fetchall()
    meses = [r[0] for r in dados]; r_vals = [r[1] for r in dados]; d_vals = [r[2] for r in dados]

    fig1, ax1 = plt.subplots(figsize=(5,3))
    ax1.plot(meses, r_vals, label="Receitas", color="green", marker="o")
    ax1.plot(meses, d_vals, label="Despesas", color="red", marker="o")
    ax1.set_title("Tendência Mensal"); ax1.legend(); ax1.tick_params(axis='x', rotation=45)
    FigureCanvasTkAgg(fig1, master=esq).get_tk_widget().pack(fill="both",expand=True)

    cur.execute("SELECT c.nome, SUM(l.valor) FROM lancamentos l JOIN categorias c ON l.categoria_id=c.id WHERE l.tipo='D' GROUP BY c.nome")
    dados_pizza = cur.fetchall()
    if dados_pizza:
        labels = [r[0] for r in dados_pizza]; valores = [r[1] for r in dados_pizza]
        fig2, ax2 = plt.subplots(figsize=(4,4))
        ax2.pie(valores, labels=labels, autopct='%1.1f%%')
        ax2.set_title("Distribuição das Despesas")
        FigureCanvasTkAgg(fig2, master=dir).get_tk_widget().pack(fill="both",expand=True)
    else:
        tk.Label(dir,text="Sem dados de despesas.").pack()

    cur.connection.close()