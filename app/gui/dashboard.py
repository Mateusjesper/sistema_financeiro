# app/gui/dashboard.py

from app.gui.receitas import tela_receitas
from app.gui.despesas import tela_despesas
from app.gui.relatorio import tela_relatorio
from app.gui.orcamento import tela_orcamento
from app.gui.usuarios import tela_usuarios
from app.gui.lancamento import gerenciar_lancamentos
from app.gui.backup import tela_backup

import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Conexão com banco
def conectar():
    return sqlite3.connect("igreja.db")

# Totais para os cards
def obter_totais():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("SELECT IFNULL(SUM(valor), 0) FROM lancamentos WHERE tipo = 'R'")
    receitas = cur.fetchone()[0]

    cur.execute("SELECT IFNULL(SUM(valor), 0) FROM lancamentos WHERE tipo = 'D'")
    despesas = cur.fetchone()[0]

    saldo = receitas - despesas

    hoje = datetime.today()
    cur.execute("SELECT IFNULL(valor, 0) FROM orcamentos WHERE mes = ? AND ano = ?", (hoje.month, hoje.year))
    orcamento_row = cur.fetchone()
    orcamento = orcamento_row[0] if orcamento_row else 0

    conn.close()
    return receitas, despesas, saldo, orcamento

# Receitas por categoria
def obter_distribuicao_receitas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.nome, SUM(l.valor) FROM lancamentos l
        JOIN categorias c ON c.id = l.categoria_id
        WHERE l.tipo = 'R'
        GROUP BY c.nome
    """)
    dados = cur.fetchall()
    conn.close()
    return dados

# Movimentações recentes
def obter_lancamentos_recentes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.data, l.tipo, l.valor, c.nome, l.descricao
        FROM lancamentos l
        LEFT JOIN categorias c ON c.id = l.categoria_id
        ORDER BY l.data DESC
        LIMIT 5
    """)
    dados = cur.fetchall()
    conn.close()
    return dados

# Interface
def abrir_dashboard(usuario: dict):
    perfil = usuario.get("perfil_id")
    nome_usuario = usuario.get("nome")

    root = tk.Tk()
    root.title("Sistema Financeiro - Primeira Igreja Batista em Catu")
    root.geometry("1200x750")
    root.configure(bg="#0b1e39")

    # Topo
    top_frame = tk.Frame(root, bg="#0b1e39", height=60)
    top_frame.pack(fill="x")

    titulo = tk.Label(top_frame, text="Sistema Financeiro - Primeira Igreja Batista em Catu", font=("Arial",14,"bold"), fg="white", bg="#0b1e39")
    titulo.place(x=20, y=15)

    usuario_lbl = tk.Label(top_frame, text=f"{nome_usuario} (USUÁRIO)", fg="white", font=("Arial", 10), bg="#0b1e39")
    usuario_lbl.place(relx=0.75, y=20)

    sair_btn = tk.Button(top_frame, text="Sair", bg="#dc3545", fg="white", command=lambda: [root.destroy(), voltar_login()])
    sair_btn.place(relx=0.92, y=15)

    # Menu lateral
    menu_frame = tk.Frame(root, bg="#0b1e39", width=180)
    menu_frame.pack(side="left", fill="y")

    tk.Label(menu_frame, text="MENU", fg="white", bg="#0b1e39", font=("Arial", 12, "bold")).pack(pady=15)

    botoes = [
        ("RECEITAS", lambda: [tela_receitas(), atualizar_dashboard()]),
        ("DESPESAS", lambda: [tela_despesas(), atualizar_dashboard()]),
        ("RELATÓRIO", lambda: tela_relatorio()),
        ("ORÇAMENTO", lambda: [tela_orcamento(usuario.get("id")), atualizar_dashboard()]),
        ("BACKUP", lambda: tela_backup()),
        ("LANÇAMENTOS", lambda: [gerenciar_lancamentos(usuario.get("id")), atualizar_dashboard()]),
    ]

    if perfil == 1:
        botoes.append(("USUÁRIOS", lambda: tela_usuarios()))

    for texto, cmd in botoes:
        tk.Button(menu_frame, text=texto, command=cmd, bg="#2e5999", fg="white", font=("Arial", 10), relief="flat",
                  width=20, height=2).pack(pady=5)

    # Painel principal
    painel_frame = tk.Frame(root, bg="#0b1e39")
    painel_frame.pack(fill="both", expand=True, padx=10, pady=10)

    cards_frame = tk.Frame(painel_frame, bg="#0b1e39")
    cards_frame.pack(pady=10)

    def card(parent, label, value, bg):
        frame = tk.Frame(parent, bg=bg, width=220, height=80, highlightbackground="#ccc", highlightthickness=1)
        frame.pack_propagate(False)
        frame.pack(side="left", padx=15)
        tk.Label(frame, text=label, bg=bg, fg="white", font=("Arial", 10)).pack(anchor="w", padx=10, pady=(5, 0))
        tk.Label(frame, text=f"R$ {value:.2f}" if isinstance(value, float) else value, bg=bg, fg="white", font=("Arial", 14, "bold")).pack(anchor="w", padx=10)

    def atualizar_dashboard():
        receitas, despesas, saldo, orcamento = obter_totais()
        for widget in cards_frame.winfo_children():
            widget.destroy()
        card(cards_frame, "Receitas", receitas, "#198754")
        card(cards_frame, "Despesas", despesas, "#dc3545")
        card(cards_frame, "Saldo", saldo, "#0d6efd")
        card(cards_frame, "Orçado", orcamento, "#ffc107")

    atualizar_dashboard()

    conteudo_frame = tk.Frame(painel_frame, bg="#0b1e39")
    conteudo_frame.pack(fill="both", expand=True, padx=20, pady=10)

    graf_frame1 = tk.Frame(conteudo_frame, bg="white", bd=1, relief="solid")
    graf_frame1.pack(side="left", expand=True, fill="both", padx=10, pady=10)

    graf_frame2 = tk.Frame(conteudo_frame, bg="white", bd=1, relief="solid")
    graf_frame2.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    # Gráfico de barras
    fig1, ax1 = plt.subplots(figsize=(4, 3))
    categorias = ["Receitas", "Despesas", "Orçado", "Saldo"]
    valores = obter_totais()
    cores = ["#198754", "#dc3545", "#ffc107", "#0d6efd"]
    ax1.bar(categorias, valores, color=cores)
    ax1.set_title("Resumo Geral")
    ax1.set_ylabel("Valor (R$)")
    fig1.tight_layout()

    canvas1 = FigureCanvasTkAgg(fig1, master=graf_frame1)
    canvas1.draw()
    canvas1.get_tk_widget().pack(expand=True)

    # Gráfico de pizza
    dados_pizza = obter_distribuicao_receitas()
    if dados_pizza:
        labels, valores = zip(*dados_pizza)
    else:
        labels, valores = ["Sem dados"], [1]

    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.pie(valores, labels=labels, autopct="%1.1f%%", startangle=140)
    ax2.set_title("Receitas por Categoria")
    fig2.tight_layout()

    canvas2 = FigureCanvasTkAgg(fig2, master=graf_frame2)
    canvas2.draw()
    canvas2.get_tk_widget().pack(expand=True)

    # Tabela
    tabela_frame = tk.Frame(painel_frame, bg="white", bd=1, relief="solid")
    tabela_frame.pack(fill="x", padx=20, pady=(0, 10))

    tk.Label(tabela_frame, text="Movimentações Recentes", bg="white", fg="#0d6efd", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(10, 0))

    colunas = ("Data", "Tipo", "Valor", "Categoria", "Descrição")
    tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings")
    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, anchor="center")
    tree.pack(fill="x", padx=10, pady=10)

    for linha in obter_lancamentos_recentes():
        tree.insert("", "end", values=linha)

    root.mainloop()

def voltar_login():
    from app.gui.login import iniciar_login
    iniciar_login()
