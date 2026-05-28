import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from scipy.optimize import milp, LinearConstraint, Bounds, linprog
from Protein import Protein
from Window import ResultsWindow
from dataset_loader import DatasetDialog, search_foods


class OptimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Dieta - Programação Linear")
        self.root.geometry("700x500")

        self.foods = []
        self.food_counter = 1
        self._ac_popup = None
        self._ac_lb = None
        self._ac_foods = []
        self._setup_ui()

    def _setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)

        input_frame = ttk.LabelFrame(self.root, text="1. Cadastro de Alimentos", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        ttk.Label(input_frame, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_name = ttk.Entry(input_frame, width=25)
        self.ent_name.grid(row=0, column=1, sticky="ew", pady=2, padx=5)
        self.ent_name.bind("<KeyRelease>", self._ac_on_key)
        self.ent_name.bind("<Down>",       self._ac_focus_list)
        self.ent_name.bind("<Escape>",     lambda e: self._ac_hide())
        self.ent_name.bind("<FocusOut>",   lambda e: self.root.after(120, self._ac_maybe_hide))

        ttk.Label(input_frame, text="Preço (R$):").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_price = ttk.Entry(input_frame, width=15)
        self.ent_price.grid(row=1, column=1, sticky="w", pady=2)

        ttk.Label(input_frame, text="Gramas/Und:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_grams = ttk.Entry(input_frame, width=15)
        self.ent_grams.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(input_frame, text="Prot/Und (g):").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_prot = ttk.Entry(input_frame, width=15)
        self.ent_prot.grid(row=3, column=1, sticky="w", pady=2)

        btn_row = ttk.Frame(input_frame)
        btn_row.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        btn_row.grid_columnconfigure(0, weight=1)
        btn_row.grid_columnconfigure(1, weight=1)
        ttk.Button(btn_row, text="➕ Adicionar à Lista",  command=self._add_food).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(btn_row, text="📦 Carregar Dataset",   command=self._open_dataset).grid(row=0, column=1, sticky="ew")

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

        ttk.Button(param_frame, text="🚀 Rodar Otimização", command=self._run_optimization,
                   style="Accent.TButton").grid(row=0, column=4, padx=10, sticky="ew")

        input_frame.grid_columnconfigure(1, weight=1)

    # ── Autocomplete ──────────────────────────────────────────────────────────

    def _ac_on_key(self, event):
        if event.keysym in ("Down", "Up", "Return", "Escape", "Tab",
                             "Left", "Right", "Home", "End", "Delete", "BackSpace"):
            if event.keysym == "BackSpace":
                # re-search after deletion
                self.root.after(10, self._ac_search)
            return
        self._ac_search()

    def _ac_search(self):
        q = self.ent_name.get().strip()
        if not q:
            self._ac_hide()
            return
        matches = search_foods(q)[:10]
        if not matches:
            self._ac_hide()
            return
        self._ac_show(matches)

    def _ac_show(self, foods):
        self._ac_foods = foods

        if self._ac_popup is None or not self._ac_popup.winfo_exists():
            self._ac_popup = tk.Toplevel(self.root)
            self._ac_popup.overrideredirect(True)
            self._ac_popup.configure(bg="#1565C0")

            self._ac_lb = tk.Listbox(
                self._ac_popup,
                font=("Segoe UI", 10),
                bg="#FFFFFF", fg="#1A237E",
                selectbackground="#1565C0", selectforeground="white",
                borderwidth=0, activestyle="none",
                relief="flat", cursor="hand2",
            )
            self._ac_lb.pack(fill="both", expand=True, padx=1, pady=1)
            self._ac_lb.bind("<ButtonRelease-1>", self._ac_select)
            self._ac_lb.bind("<Return>",           self._ac_select)
            self._ac_lb.bind("<Escape>",           self._ac_escape)
            self._ac_lb.bind("<FocusOut>",         lambda e: self.root.after(120, self._ac_maybe_hide))

        self._ac_lb.delete(0, tk.END)
        for f in foods:
            self._ac_lb.insert(
                tk.END,
                f"  {f.name:<46}  {f.protein_grams}g prot | R${f.price:.2f}"
            )

        self.root.update_idletasks()
        x = self.ent_name.winfo_rootx()
        y = self.ent_name.winfo_rooty() + self.ent_name.winfo_height() + 1
        w = max(self.ent_name.winfo_width(), 480)
        h = min(len(foods), 8) * 22 + 2
        self._ac_popup.geometry(f"{w}x{h}+{x}+{y}")
        self._ac_popup.lift()

    def _ac_hide(self):
        if self._ac_popup and self._ac_popup.winfo_exists():
            self._ac_popup.destroy()
        self._ac_popup = None
        self._ac_lb = None

    def _ac_maybe_hide(self):
        try:
            focused = self.root.focus_get()
        except Exception:
            focused = None
        if focused is not self._ac_lb and focused is not self.ent_name:
            self._ac_hide()

    def _ac_focus_list(self, event=None):
        if self._ac_lb and self._ac_popup.winfo_exists():
            self._ac_lb.focus_set()
            self._ac_lb.selection_set(0)
            self._ac_lb.activate(0)
        return "break"

    def _ac_select(self, event=None):
        if not self._ac_lb:
            return
        sel = self._ac_lb.curselection()
        if not sel:
            return
        food = self._ac_foods[sel[0]]
        self.ent_name.delete(0, tk.END)
        self.ent_name.insert(0, food.name)
        self.ent_price.delete(0, tk.END)
        self.ent_price.insert(0, str(food.price))
        self.ent_grams.delete(0, tk.END)
        self.ent_grams.insert(0, str(food.grams))
        self.ent_prot.delete(0, tk.END)
        self.ent_prot.insert(0, str(food.protein_grams))
        self._ac_hide()
        self.ent_price.focus_set()

    def _ac_escape(self, event=None):
        self._ac_hide()
        self.ent_name.focus_set()

    # ── Food management ───────────────────────────────────────────────────────

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

    def _open_dataset(self):
        DatasetDialog(self.root, self._add_from_dataset)

    def _add_from_dataset(self, food):
        self.foods.append(food)
        self.lb_foods.insert(tk.END, repr(food))
        self.food_counter += 1
