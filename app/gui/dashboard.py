# app/gui/dashboard.py

# Importa as telas dos módulos
from app.gui.receitas import tela_receitas
from app.gui.despesas import tela_despesas
from app.gui.relatorio import tela_relatorio
from app.gui.graficos import tela_graficos
from app.gui.orcamento import tela_orcamento
from app.gui.usuarios import tela_usuarios
from app.gui.lancamento import gerenciar_lancamentos
from app.gui.login import iniciar_login  # Importação para logout

import tkinter as tk

def abrir_dashboard(usuario: dict):
    perfil = usuario.get("perfil_id")  # 1=Admin, 2=Pastor, 3=Tesoureiro, 4=Secretária

    root = tk.Tk()
    root.title("Painel Financeiro")
    root.geometry("1000x600")
    root.configure(bg="#f8f9fa")

    # Topo da tela
    top_frame = tk.Frame(root, bg="#0d6efd", height=50)
    top_frame.pack(side="top", fill="x")

    # Botão de logout
    logout_btn = tk.Button(top_frame, text="Sair", bg="#dc3545", fg="white",
                           command=lambda: [root.destroy(), iniciar_login()])
    logout_btn.pack(side="right", padx=10, pady=10)

    # Nome do usuário
    nome_lbl = tk.Label(top_frame, text=f"Bem-vindo, {usuario.get('nome')}",
                        bg="#0d6efd", fg="white", font=("Arial", 10, "bold"))
    nome_lbl.pack(side="left", padx=10)

    # Botões centrais (exemplo)
    botoes = [
        ("Receitas", lambda: tela_receitas()),
        ("Despesas", lambda: tela_despesas()),
        ("Relatório", lambda: tela_relatorio()),
        ("Gráficos", lambda: tela_graficos()),
        ("Orçamento", lambda: tela_orcamento(usuario.get("id"))),
        ("Backup", lambda: abrir_tela_backup()),  # ⚠️ Usar função interna
        ("Lançamentos", lambda: gerenciar_lancamentos(usuario.get("id"))),
    ]

    if perfil == 1:  # Admin
        botoes.append(("Usuários", lambda: tela_usuarios()))

    btn_frame = tk.Frame(root, bg="#f8f9fa")
    btn_frame.pack(pady=20)

    for texto, cmd in botoes:
        btn = tk.Button(btn_frame, text=texto, command=cmd, width=20, height=2, bg="#198754", fg="white")
        btn.pack(pady=5)

    root.mainloop()

def abrir_tela_backup():
    from app.gui.backup import tela_backup
    tela_backup()
