# app/gui/backup.py

import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import shutil
import os

from app.banco import conectar

def tela_backup():
    win = tk.Toplevel()
    win.title("Backup Manual")
    win.geometry("400x200")

    tk.Label(win, text="Backup do Banco de Dados", font=("Arial", 14)).pack(pady=10)

    def fazer_backup():
        try:
            destino = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Banco SQLite", "*.db")])
            if not destino:
                return

            caminho_db = os.path.join("app", "data", "banco.db")  # ajuste para seu caminho real
            shutil.copy2(caminho_db, destino)

            messagebox.showinfo("Sucesso", "Backup realizado com sucesso.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(win, text="Selecionar destino e salvar", command=fazer_backup,
              bg="#0d6efd", fg="white").pack(pady=20)
