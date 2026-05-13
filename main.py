import tkinter as tk
from tkinter import ttk, messagebox
from Protein import Protein
from Optimization import OptimizationApp

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    app = OptimizationApp(root)
    root.mainloop()