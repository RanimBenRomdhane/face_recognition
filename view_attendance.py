import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_PATH = 'employees.db'

def open_view_attendance_window(master):
    window = tk.Toplevel(master)
    window.title("📆 Historique de présence")
    window.state("zoomed")
    window.configure(bg="#f1f3f6")

    # Modale et focus
    window.transient(master)
    window.grab_set()
    window.focus_set()

    def on_close():
        window.grab_release()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    tk.Label(
        window,
        text="📆 Historique des présences",
        font=("Segoe UI", 26, "bold"),
        bg="#f1f3f6",
        fg="#2c3e50"
    ).pack(pady=30)

    frame_table = tk.Frame(window, bg="white", bd=2, relief="groove")
    frame_table.pack(padx=40, pady=10, fill="both", expand=True)

    columns = ("ID", "CIN", "Date", "Heure de pointage")
    tree = ttk.Treeview(frame_table, columns=columns, show="headings")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)

    for col in columns:
        width = 150 if col == "Heure de pointage" else 120
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=width)

    scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side='right', fill='y')
    tree.pack(fill="both", expand=True)

    def load_attendance():
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM attendance ORDER BY date DESC, time_in DESC")
                rows = c.fetchall()

            for row in tree.get_children():
                tree.delete(row)

            for row in rows:
                tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger les présences : {str(e)}")

    load_attendance()

    btn_frame = tk.Frame(window, bg="#f1f3f6")
    btn_frame.pack(pady=50)

    btn_refresh = tk.Button(
        btn_frame,
        text="🔄 Rafraîchir les données",
        command=load_attendance,
        font=("Segoe UI", 12),
        bg="#007BFF",
        fg="white",
        padx=20,
        pady=10,
        relief="raised",
        cursor="hand2"
    )
    btn_refresh.grid(row=0, column=0, padx=10)

    btn_return = tk.Button(
        btn_frame,
        text="↩ Retour au menu",
        command=on_close,
        font=("Segoe UI", 12),
        bg="#6c757d",
        fg="white",
        padx=20,
        pady=10,
        relief="raised",
        cursor="hand2"
    )
    btn_return.grid(row=0, column=1, padx=10)
