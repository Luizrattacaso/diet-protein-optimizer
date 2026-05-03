import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy.optimize import linprog
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ==========================================
# 0. CLASSE BASE (FORNECIDA POR VOCÊ)
# ==========================================
class Protein:
    def __init__(self, name, price, grams, protein_grams):
        self.name = name
        self.price = price
        self.grams = grams
        self.protein_grams = protein_grams  # Total de proteína por unidade/embalagem

    def get_price(self): return self.price
    def get_grams(self): return self.grams
    def get_protein(self): return self.protein_grams

    def price_per_gram(self):
        return self.price / self.grams if self.grams > 0 else float('inf')

    def protein_density(self):
        return self.protein_grams / self.grams if self.grams > 0 else 0.0

    def __repr__(self):
        return f"{self.name} | {self.grams}g | R${self.price:.2f} | {self.protein_grams}g prot"

# ==========================================
# 1. JANELA DE RESULTADOS (Seção 3 e 4)
# ==========================================
class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, foods, x_opt, target_prot, budget):
        super().__init__(parent)
        self.title("Resultado da Otimização")
        self.geometry("900x800")
        
        self.foods = foods
        self.x_opt = x_opt
        self.target_prot = target_prot
        self.budget = budget
        
        self._setup_ui()
        self._display_math()
        self._plot_graph()

    def _setup_ui(self):
        # Seção 3: Matemática
        res_frame = ttk.LabelFrame(self, text="3. Formulação Matemática e Resultados", padding=15)
        res_frame.pack(fill="x", padx=20, pady=10)

        self.txt_math = tk.Text(res_frame, height=12, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_math.pack(fill="both", expand=True)

        # Seção 4: Gráfico
        graph_frame = ttk.LabelFrame(self, text="4. Visualização do Ponto Ótimo", padding=15)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _display_math(self):
        c = [f.price for f in self.foods]
        vars_str = f"x_i = quantidade (unidades/embalagens) do alimento {', '.join([f.name for f in self.foods])}"
        
        obj_str = "Minimizar Z (Custo Total) = " + " + ".join([f"{f.price}*x_{i+1}" for i, f in enumerate(self.foods)])
        constr_prot = " + ".join([f"{f.protein_grams}*x_{i+1}" for i, f in enumerate(self.foods)])
        constr_budget = " + ".join([f"{f.price}*x_{i+1}" for i, f in enumerate(self.foods)])
        
        math_text = (
            f" FORMULAÇÃO DO MODELO LINEAR\n"
            f"{'='*50}\n"
            f"VARIÁVEIS DE DECISÃO:\n{vars_str}\n\n"
            f"FUNÇÃO OBJETIVO:\n{obj_str}\n\n"
            f"RESTRIÇÕES:\n"
            f"1. Proteína Mínima: {constr_prot} ≥ {self.target_prot}\n"
            f"2. Orçamento Máximo: {constr_budget} ≤ {self.budget}\n"
            f"3. Não-negatividade: x_i ≥ 0, ∀i\n\n"
            f"🔄 FORMA PADRÃO (Solver):\n"
            f"min cᵀx  sujeito a  A_ub·x ≤ b_ub,  x ≥ 0\n"
            f"• c = {c}\n"
            f"• A_ub[0] = {[-f.protein_grams for f in self.foods]}  (proteína * -1)\n"
            f"• A_ub[1] = {[f.price for f in self.foods]}\n"
            f"• b_ub = [{-self.target_prot}, {self.budget}]\n\n"
            f"✅ RESULTADO ÓTIMO:\n"
        )
        
        for f, val in zip(self.foods, self.x_opt):
            math_text += f"  • {f.name}: {val:.2f} un. | Custo: R${val*f.price:.2f} | Prot: {val*f.protein_grams:.1f}g\n"
        
        total_cost = sum(f.price * val for f, val in zip(self.foods, self.x_opt))
        total_prot = sum(f.protein_grams * val for f, val in zip(self.foods, self.x_opt))
        math_text += f"\n💰 Custo Total: R${total_cost:.2f}\n🥩 Proteína Total: {total_prot:.1f}g"
        
        self.txt_math.insert(tk.END, math_text)

    def _plot_graph(self):
        self.ax.clear()
        
        if len(self.foods) == 2:
            f1, f2 = self.foods[0], self.foods[1]
            x = np.linspace(0, max(self.x_opt[0]*2, self.budget/f1.price if f1.price>0 else 10), 100)
            
            y_prot = np.where(f2.protein_grams != 0, (self.target_prot - f1.protein_grams*x) / f2.protein_grams, 0)
            y_budget = np.where(f2.price != 0, (self.budget - f1.price*x) / f2.price, 0)
            
            self.ax.plot(x, y_prot, 'r--', label=f'Proteína (≥ {self.target_prot}g)')
            self.ax.plot(x, y_budget, 'g--', label=f'Orçamento (≤ R${self.budget})')
            
            x1_vals = x[(y_prot >= 0) & (y_budget >= 0) & (y_prot <= y_budget)]
            if len(x1_vals) > 0:
                y1_vals = y_prot[(y_prot >= 0) & (y_budget >= 0) & (y_prot <= y_budget)]
                self.ax.fill_between(x1_vals, y1_vals, 0, color='skyblue', alpha=0.3, label='Região Viável')
            
            self.ax.plot(self.x_opt[0], self.x_opt[1], 'ko', markersize=10, label=f'Ponto Ótimo')
            self.ax.set_xlabel(f"Qtd {f1.name}")
            self.ax.set_ylabel(f"Qtd {f2.name}")
            
        else:
            names = [f.name for f in self.foods]
            quantities = list(self.x_opt)
            costs = [f.price * q for f, q in zip(self.foods, self.x_opt)]
            
            x_pos = np.arange(len(names))
            self.ax.bar(x_pos - 0.2, quantities, 0.4, label='Quantidade', color='#4CAF50')
            self.ax.bar(x_pos + 0.2, costs, 0.4, label='Custo (R$)', color='#2196F3')
            
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(names)
            self.ax.set_ylabel("Valor / Quantidade")
            self.ax.legend()

        self.ax.grid(True, alpha=0.3)
        self.ax.set_title("Otimização Linear - Resultados")
        self.ax.legend(loc='upper right')
        self.fig.tight_layout()
        self.canvas.draw()

# ==========================================
# 2. JANELA PRINCIPAL (Inputs)
# ==========================================
class OptimizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Dieta - Programação Linear")
        self.root.geometry("700x450")
        
        self.foods = []
        self.food_counter = 1
        self._setup_ui()

    def _setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)

        # Frame de Input
        input_frame = ttk.LabelFrame(self.root, text="1. Cadastro de Alimentos", padding=15)
        input_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        # Grid de Inputs (2 colunas)
        # Linha 1
        ttk.Label(input_frame, text="Nome:").grid(row=0, column=0, sticky="w", pady=2)
        self.ent_name = ttk.Entry(input_frame, width=25)
        self.ent_name.grid(row=0, column=1, sticky="ew", pady=2, padx=5)

        ttk.Label(input_frame, text="Preço (R$):").grid(row=1, column=0, sticky="w", pady=2)
        self.ent_price = ttk.Entry(input_frame, width=15)
        self.ent_price.grid(row=1, column=1, sticky="w", pady=2)

        # Linha 2
        ttk.Label(input_frame, text="Gramas/Und:").grid(row=2, column=0, sticky="w", pady=2)
        self.ent_grams = ttk.Entry(input_frame, width=15)
        self.ent_grams.grid(row=2, column=1, sticky="w", pady=2)

        ttk.Label(input_frame, text="Prot/Und (g):").grid(row=3, column=0, sticky="w", pady=2)
        self.ent_prot = ttk.Entry(input_frame, width=15)
        self.ent_prot.grid(row=3, column=1, sticky="w", pady=2)

        # Botão Adicionar
        ttk.Button(input_frame, text="➕ Adicionar à Lista", command=self._add_food).grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Lista
        self.lb_foods = tk.Listbox(input_frame, height=6, font=("Arial", 10))
        self.lb_foods.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5)

        # Frame de Parâmetros
        param_frame = ttk.LabelFrame(self.root, text="2. Parâmetros da Otimização", padding=15)
        param_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")

        # Grid de Parâmetros
        ttk.Label(param_frame, text="Meta de Proteína (g):").grid(row=0, column=0, sticky="w", padx=5)
        self.ent_target_prot = ttk.Entry(param_frame, width=15)
        self.ent_target_prot.insert(0, "150")
        self.ent_target_prot.grid(row=0, column=1, sticky="w")

        ttk.Label(param_frame, text="Orçamento Máx. (R$):").grid(row=0, column=2, sticky="w", padx=15)
        self.ent_budget = ttk.Entry(param_frame, width=15)
        self.ent_budget.insert(0, "50")
        self.ent_budget.grid(row=0, column=3, sticky="w")

        ttk.Button(param_frame, text=" Rodar Otimização", command=self._run_optimization, style="Accent.TButton").grid(row=0, column=4, padx=10, sticky="ew")
        
        # Configurar pesos do grid
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

        # Preparar vetores
        c = [f.price for f in self.foods]
        
        A_ub = [
            [-f.protein_grams for f in self.foods],
            [f.price for f in self.foods]
        ]
        b_ub = [-target_prot, budget]
        bounds = [(0, None) for _ in self.foods]

        res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')

        if not res.success:
            messagebox.showerror("Inviável", "Não existe solução que atenda às restrições (proteína muito alta ou orçamento muito baixo).")
            return

        # Abrir nova janela de resultados
        ResultsWindow(self.root, self.foods, res.x, target_prot, budget)

if __name__ == "__main__":
    root = tk.Tk()
    # Estilização básica
    style = ttk.Style()
    style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    app = OptimizationApp(root)
    root.mainloop()