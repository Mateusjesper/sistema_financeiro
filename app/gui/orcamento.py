import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from app.banco import conectar


def tela_orcamento(usuario_id):
    win = tk.Toplevel()
    win.title("Orçamento Mensal")
    win.geometry("400x360")

    tk.Label(win, text="Orçamento do Mês", font=("Arial", 14)).pack(pady=10)

    frame = tk.Frame(win)
    frame.pack(pady=10)

    # Entradas
    tk.Label(frame, text="Mês (1-12):").grid(row=0, column=0, sticky="e")
    mes_entry = tk.Entry(frame, width=5)
    mes_entry.insert(0, datetime.now().month)
    mes_entry.grid(row=0, column=1)

    tk.Label(frame, text="Ano:").grid(row=1, column=0, sticky="e")
    ano_entry = tk.Entry(frame, width=5)
    ano_entry.insert(0, datetime.now().year)
    ano_entry.grid(row=1, column=1)

    tk.Label(frame, text="Valor Orçado (R$):").grid(row=2, column=0, sticky="e")
    valor_entry = tk.Entry(frame)
    valor_entry.grid(row=2, column=1)

    result_label = tk.Label(win, text="", font=("Arial", 10))
    result_label.pack(pady=10)

    def salvar_orcamento():
        try:
            mes = int(mes_entry.get())
            ano = int(ano_entry.get())
            valor = float(valor_entry.get().replace(",", "."))

            if mes < 1 or mes > 12:
                raise ValueError("Mês inválido. Use um valor de 1 a 12.")

            conn = conectar()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO orcamentos (mes, ano, valor, criado_por)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(mes, ano) DO UPDATE SET valor = excluded.valor
            """, (mes, ano, valor, usuario_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Orçamento salvo com sucesso.")
            consultar()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def consultar():
        try:
            mes = int(mes_entry.get())
            ano = int(ano_entry.get())

            conn = conectar()
            cur = conn.cursor()

            #Valor orçado
            cur.execute("SELECT valor FROM orcamentos WHERE mes=? AND ano=?", (mes, ano))
            row = cur.fetchone()
            orcado = row[0] if row else 0

            #Total de despesas
            cur.execute("""
                SELECT SUM(valor) FROM lancamentos
                WHERE tipo='D' AND strftime('%m', data)=? AND strftime('%Y', data)=?
            """, (f"{mes:02}", str(ano)))
            gasto = cur.fetchone()[0] or 0

            restante = orcado - gasto
            status = "DENTRO do orçamento" if restante >= 0 else "ACIMA do orçamento"
            cor = "green" if restante >= 0 else "red"

            result = f"Orçado: R$ {orcado:,.2f}\nGasto: R$ {gasto:,.2f}\nDiferença: R$ {restante:,.2f} ({status})"
            result_label.config(text=result, fg=cor)
            conn.close()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # Botões
    tk.Button(win, text="Salvar Orçamento", command=salvar_orcamento,
              bg="#0d6efd", fg="white", width=20).pack(pady=5)
    tk.Button(win, text="Consultar Situação", command=consultar,
              width=20).pack(pady=5)
