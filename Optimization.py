import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from scipy.optimize import milp, LinearConstraint, Bounds, linprog
from Protein import Protein
from Window import ResultsWindow

class OptimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Dieta - Programação Linear")
        self.root.geometry("700x500")
        
        self.foods = []
        self.food_counter = 1
        self._setup_ui()

    def _setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)

        input_frame = ttk.LabelFrame(self.root, text="1. Cadastro de Alimentos", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_name = ttk.Entry(input_frame, width=25)
        self.ent_name.grid(row=0, column=1, sticky="ew", pady=2, padx=5)

        ttk.Label(input_frame, text="Preço (R$):").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_price = ttk.Entry(input_frame, width=15)
        self.ent_price.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(input_frame, text="Gramas/Und:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_grams = ttk.Entry(input_frame, width=15)
        self.ent_grams.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(input_frame, text="Prot/Und (g):").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_prot = ttk.Entry(input_frame, width=15)
        self.ent_prot.grid(row=3, column=1, sticky="w", pady=2)

        ttk.Button(input_frame, text="➕ Adicionar à Lista", command=self._add_food).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        self.lb_foods = tk.Listbox(input_frame, height=6, font=("Arial", 10))
        self.lb_foods.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        param_frame = ttk.LabelFrame(self.root, text="2. Parâmetros da Otimização", padding=15)
        param_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        ttk.Label(param_frame, text="Meta de Proteína (g):").grid(row=0, column=0, sticky="w", padx=5)
        self.ent_target_prot = ttk.Entry(param_frame, width=15)
        self.ent_target_prot.insert(0, "150")
        self.ent_target_prot.grid(row=0, column=1, sticky="w")

        ttk.Label(param_frame, text="Orçamento Máx. (R$):").grid(row=0, column=2, sticky="w", padx=15)
        self.ent_budget = ttk.Entry(param_frame, width=15)
        self.ent_budget.insert(0, "50")
        self.ent_budget.grid(row=0, column=3, sticky="w")

        ttk.Button(param_frame, text="🚀 Rodar Otimização", command=self._run_optimization, style="Accent.TButton").grid(row=0, column=4, padx=10, sticky="ew")
        
        input_frame.grid_columnconfigure(1, weight=1)

    def _add_food(self):
        try:
            name = self.ent_name.get().strip() or f"Alimento {self.food_counter}"
            price = float(self.ent_price.get())
            grams = float(self.ent_grams.get())
            prot = float(self.ent_prot.get())
            if price <= 0 or grams <= 0 or prot < 0:
                raise ValueError
            food = Protein(name, price, grams, prot)
            self.foods.append(food)
            self.lb_foods.insert(tk.END, repr(food))
            self.food_counter += 1
            self._clear_inputs()
        except ValueError:
            messagebox.showerror("Erro", "Preencha todos os campos com valores válidos (>0).")

    def _clear_inputs(self):
        for ent in [self.ent_name, self.ent_price, self.ent_grams, self.ent_prot]:
            ent.delete(0, tk.END)
        self.ent_name.focus()

    def _run_optimization(self):
        if len(self.foods) < 1:
            messagebox.showwarning("Atenção", "Adicione pelo menos 1 alimento.")
            return

        try:
            target_prot = float(self.ent_target_prot.get())
            budget = float(self.ent_budget.get())
        except ValueError:
            messagebox.showerror("Erro", "Meta de proteína e orçamento devem ser números.")
            return

        c = np.array([f.price for f in self.foods])
        A = np.array([
            [f.protein_grams for f in self.foods],
            [f.price for f in self.foods]
        ], dtype=float)

        constraints = LinearConstraint(A, lb=[target_prot, -np.inf], ub=[np.inf, budget])
        integrality = np.ones(len(self.foods))
        bounds = Bounds(lb=0)

        res = milp(c, constraints=constraints, integrality=integrality, bounds=bounds)

        if not res.success:
            messagebox.showerror("Inviável", "Não existe solução que atenda às restrições.")
            return

        ResultsWindow(self.root, self.foods, np.maximum(np.round(res.x), 0), target_prot, budget)