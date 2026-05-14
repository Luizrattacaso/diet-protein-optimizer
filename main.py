import tkinter as tk
from tkinter import ttk, messagebox
from Protein import Protein
from Optimization import OptimizationApp

_BG      = "#F0F4F8"
_PRIMARY = "#1565C0"
_ACCENT  = "#2E7D32"

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=_BG)

    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".",
        background=_BG,
        font=("Segoe UI", 10))
    style.configure("TFrame",        background=_BG)
    style.configure("TLabel",        background=_BG, foreground="#212121",
                                     font=("Segoe UI", 10))
    style.configure("TLabelframe",   background=_BG, bordercolor="#CBD5E0")
    style.configure("TLabelframe.Label",
        font=("Segoe UI", 10, "bold"),
        foreground=_PRIMARY,
        background=_BG)
    style.configure("TEntry",        font=("Segoe UI", 10), fieldbackground="#FFFFFF")
    style.configure("TScrollbar",
        background="#E2E8F0", troughcolor="#EDF2F7",
        bordercolor=_BG, arrowcolor="#4A5568")

    style.configure("Add.TButton",
        font=("Segoe UI", 10),
        background=_PRIMARY, foreground="white",
        bordercolor=_PRIMARY, padding=(8, 5))
    style.map("Add.TButton",
        background=[("active", "#0D47A1"), ("pressed", "#0A3069")],
        foreground=[("active", "white"),   ("pressed", "white")])

    style.configure("Accent.TButton",
        font=("Segoe UI", 11, "bold"),
        background=_ACCENT, foreground="white",
        bordercolor=_ACCENT, padding=(12, 7))
    style.map("Accent.TButton",
        background=[("active", "#1B5E20"), ("pressed", "#145214")],
        foreground=[("active", "white"),   ("pressed", "white")])

    app = OptimizationApp(root)
    root.mainloop()
