import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon
from scipy.optimize import linprog

class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, foods, x_opt, target_prot, budget):
        super().__init__(parent)
        self.title("Resultado da Otimização - Resolução Gráfica")
        self.geometry("1100x900")
        
        self.foods = foods
        self.x_opt = x_opt
        self.target_prot = target_prot
        self.budget = budget
        
        self._setup_ui()
        self._display_math()
        self._plot_graph()
        self._compute_sensitivity()
        self._display_sensitivity()

    def _setup_ui(self):
        # Seção 3: Matemática
        res_frame = ttk.LabelFrame(self, text="3. Formulação Matemática e Resultados", padding=15)
        res_frame.pack(fill="x", padx=20, pady=10)

        self.txt_math = tk.Text(res_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_math.pack(fill="both", expand=True)

        # Seção 4: Gráfico de Resolução Gráfica
        graph_frame = ttk.LabelFrame(self, text="4. Resolução Gráfica - Região Viável e Ponto Ótimo", padding=15)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Seção 5: Análise de Sensibilidade
        sens_frame = ttk.LabelFrame(self, text="5. Análise de Sensibilidade", padding=15)
        sens_frame.pack(fill="x", padx=20, pady=10)

        sens_inner = tk.Frame(sens_frame)
        sens_inner.pack(fill="both", expand=True)
        self.txt_sens = tk.Text(sens_inner, height=8, wrap=tk.WORD, font=("Consolas", 10))
        scrollbar_sens = ttk.Scrollbar(sens_inner, orient="vertical", command=self.txt_sens.yview)
        self.txt_sens.configure(yscrollcommand=scrollbar_sens.set)
        self.txt_sens.pack(side="left", fill="both", expand=True)
        scrollbar_sens.pack(side="right", fill="y")

    def _display_math(self):
        c = [f.price for f in self.foods]
        vars_str = f"x_i = quantidade do alimento {', '.join([f.name for f in self.foods])}"
        
        obj_str = "Min Z = " + " + ".join([f"{f.price}x_{i+1}" for i, f in enumerate(self.foods)])
        constr_prot = " + ".join([f"{f.protein_grams}x_{i+1}" for i, f in enumerate(self.foods)])
        constr_budget = " + ".join([f"{f.price}x_{i+1}" for i, f in enumerate(self.foods)])
        
        math_text = (
            f"MODELO DE PROGRAMAÇÃO LINEAR\n"
            f"{'='*50}\n"
            f"Variáveis: {vars_str}\n\n"
            f"Função Objetivo: {obj_str}\n\n"
            f"Restrições:\n"
            f"  {constr_prot} ≥ {self.target_prot} (Proteína mínima)\n"
            f"  {constr_budget} ≤ {self.budget} (Orçamento máximo)\n"
            f"  x_i ≥ 0, x_i ∈ ℤ (Não-negatividade e integralidade)\n\n"
            f"SOLUÇÃO ÓTIMA:\n"
        )
        
        total_cost = 0
        total_prot = 0
        for f, val in zip(self.foods, self.x_opt):
            cost_item = val * f.price
            prot_item = val * f.protein_grams
            total_cost += cost_item
            total_prot += prot_item
            math_text += f"  • {f.name}: x = {int(val)} unidades\n"
            math_text += f"    Custo: R${cost_item:.2f} | Proteína: {prot_item:.1f}g\n"
        
        math_text += f"\nCusto Total: R${total_cost:.2f}\nProteína Total: {total_prot:.1f}g"
        
        self.txt_math.insert(tk.END, math_text)

    def _plot_graph(self):
        self.ax.clear()
        
        if len(self.foods) == 2:
            self._plot_2d_graph()
        else:
            self._plot_multi_graph()
        
        self.fig.tight_layout()
        self.canvas.draw()

    def _plot_2d_graph(self):
        f1, f2 = self.foods[0], self.foods[1]
        
        # Definir limites do gráfico
        max_x1 = max(self.budget / f1.price * 1.5, 
                     self.target_prot / f1.protein_grams * 1.5) if f1.price > 0 and f1.protein_grams > 0 else 10
        max_x2 = max(self.budget / f2.price * 1.5, 
                     self.target_prot / f2.protein_grams * 1.5) if f2.price > 0 and f2.protein_grams > 0 else 10
        
        x1 = np.linspace(0, max_x1, 100)

        if f2.protein_grams != 0:
            x2_prot = (self.target_prot - f1.protein_grams * x1) / f2.protein_grams
        else:
            x2_prot = np.zeros_like(x1)

        if f2.price != 0:
            x2_budget = (self.budget - f1.price * x1) / f2.price
        else:
            x2_budget = np.zeros_like(x1)
        
        self.ax.plot(x1, x2_prot, 'r-', linewidth=2, label=f'Restrição 1: Proteína ≥ {self.target_prot}g')
        self.ax.plot(x1, x2_budget, 'b-', linewidth=2, label=f'Restrição 2: Orçamento ≤ R${self.budget}')
        
        self.ax.axhline(y=0, color='k', linewidth=1)
        self.ax.axvline(x=0, color='k', linewidth=1)
        
        # Calcular vértices da região viável
        vertices = self._find_feasible_vertices(f1, f2, max_x1, max_x2)
        
        if len(vertices) > 2:
            # Preencher região viável
            feasible_region = Polygon(vertices, alpha=0.3, color='yellow', label='Região Viável')
            self.ax.add_patch(feasible_region)
            
            # Destacar vértices
            vertices_array = np.array(vertices)
            self.ax.plot(vertices_array[:, 0], vertices_array[:, 1], 'ko', markersize=6)
        
        # Plotar ponto ótimo
        opt_x1, opt_x2 = self.x_opt[0], self.x_opt[1]
        self.ax.plot(opt_x1, opt_x2, 'r*', markersize=15, markeredgewidth=2, label=f'Ponto Ótimo\n({opt_x1:.0f}, {opt_x2:.0f})')

        Z_opt = f1.price * opt_x1 + f2.price * opt_x2
        if f2.price != 0:
            x2_obj = (Z_opt - f1.price * x1) / f2.price
            self.ax.plot(x1, x2_obj, 'g--', linewidth=1.5, alpha=0.7, label=f'Função Objetivo\n(Z = R${Z_opt:.2f})')
        
        # Configurações do gráfico
        self.ax.set_xlabel(f'Quantidade de {f1.name} (x₁)', fontsize=12)
        self.ax.set_ylabel(f'Quantidade de {f2.name} (x₂)', fontsize=12)
        self.ax.set_title('RESOLUÇÃO GRÁFICA - Programação Linear Inteira', fontsize=14, fontweight='bold', pad=20)
        self.ax.legend(loc='upper right', fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_xlim(0, max_x1)
        self.ax.set_ylim(0, max_x2)
        
        info_text = (f'PONTO ÓTIMO:\n'
                    f'x₁ = {opt_x1:.0f} ({f1.name})\n'
                    f'x₂ = {opt_x2:.0f} ({f2.name})\n'
                    f'Custo: R${Z_opt:.2f}\n'
                    f'Proteína: {f1.protein_grams*opt_x1 + f2.protein_grams*opt_x2:.1f}g')
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes, 
                    fontsize=10, verticalalignment='top', 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    def _find_feasible_vertices(self, f1, f2, max_x1, max_x2):
        """Encontra os vértices da região viável"""
        vertices = []

        det = f1.protein_grams * f2.price - f2.protein_grams * f1.price
        if abs(det) > 1e-10:
            x1_int = (self.target_prot * f2.price - self.budget * f2.protein_grams) / det
            x2_int = (self.budget * f1.protein_grams - self.target_prot * f1.price) / det
            if x1_int >= 0 and x2_int >= 0:
                vertices.append((x1_int, x2_int))
        
        if f1.protein_grams > 0:
            x1_prot_axis = self.target_prot / f1.protein_grams
            if x1_prot_axis <= max_x1:
                if f1.price * x1_prot_axis <= self.budget:
                    vertices.append((x1_prot_axis, 0))
        
        if f2.protein_grams > 0:
            x2_prot_axis = self.target_prot / f2.protein_grams
            if x2_prot_axis <= max_x2:
                if f2.price * x2_prot_axis <= self.budget:
                    vertices.append((0, x2_prot_axis))
        
        if f1.price > 0:
            x1_budget_axis = self.budget / f1.price
            if x1_budget_axis <= max_x1:
                if f1.protein_grams * x1_budget_axis >= self.target_prot:
                    vertices.append((x1_budget_axis, 0))
        
        if f2.price > 0:
            x2_budget_axis = self.budget / f2.price
            if x2_budget_axis <= max_x2:
                if f2.protein_grams * x2_budget_axis >= self.target_prot:
                    vertices.append((0, x2_budget_axis))
        
        if len(vertices) > 2:
            center = (sum(v[0] for v in vertices) / len(vertices),
                     sum(v[1] for v in vertices) / len(vertices))
            vertices.sort(key=lambda v: np.arctan2(v[1] - center[1], v[0] - center[0]))
        
        return vertices

    def _plot_multi_graph(self):
        names = [f.name for f in self.foods]
        quantities = list(self.x_opt)
        costs = [f.price * q for f, q in zip(self.foods, quantities)]
        proteins = [f.protein_grams * q for f, q in zip(self.foods, quantities)]
        
        x_pos = np.arange(len(names))
        width = 0.25
        
        self.ax.bar(x_pos - width, quantities, width, label='Quantidade', color='#4CAF50')
        self.ax.bar(x_pos, costs, width, label='Custo (R$)', color='#2196F3')
        self.ax.bar(x_pos + width, proteins, width, label='Proteína (g)', color='#FF9800')
        
        self.ax.set_xticks(x_pos)
        self.ax.set_xticklabels(names, rotation=15, ha='right')
        self.ax.set_ylabel('Valor', fontsize=12)
        self.ax.set_title('Distribuição da Solução Ótima', fontsize=14, fontweight='bold')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3, axis='y')
        
        total_cost = sum(costs)
        total_prot = sum(proteins)
        self.ax.axhline(y=self.budget, color='red', linestyle='--', alpha=0.5, label=f'Orçamento Máx (R${self.budget})')
        self.ax.axhline(y=self.target_prot, color='purple', linestyle='--', alpha=0.5, label=f'Meta Proteína ({self.target_prot}g)')
        
        info_text = f'Custo Total: R${total_cost:.2f}\nProteína Total: {total_prot:.1f}g'
        self.ax.text(0.02, 0.98, info_text, transform=self.ax.transAxes,
                    fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    def _compute_sensitivity(self):
        c_lp = [f.price for f in self.foods]
        A_ub = [
            [-f.protein_grams for f in self.foods],
            [f.price for f in self.foods]
        ]
        b_ub = [-self.target_prot, self.budget]
        bounds_lp = [(0, None) for _ in self.foods]

        res_lp = linprog(c_lp, A_ub=A_ub, b_ub=b_ub, bounds=bounds_lp, method='highs')

        if res_lp.success and hasattr(res_lp, 'ineqlin'):
            self.shadow_protein = -res_lp.ineqlin.marginals[0]
            self.shadow_budget = res_lp.ineqlin.marginals[1]
            self.reduced_costs = list(res_lp.lower.marginals)
            self.lp_cost = res_lp.fun
            self.lp_x = list(res_lp.x)
            self.sens_available = True
        else:
            self.sens_available = False

    def _display_sensitivity(self):
        if not self.sens_available:
            self.txt_sens.insert(tk.END, "Análise de sensibilidade indisponível.")
            return

        ilp_cost = sum(f.price * v for f, v in zip(self.foods, self.x_opt))
        ilp_prot = sum(f.protein_grams * v for f, v in zip(self.foods, self.x_opt))
        gap_abs = ilp_cost - self.lp_cost
        gap_pct = (gap_abs / self.lp_cost * 100) if self.lp_cost > 1e-9 else 0.0

        text = (
            f"ANÁLISE DE SENSIBILIDADE\n"
            f"{'='*45}\n\n"
            f"GAP DE INTEGRALIDADE:\n"
            f"  Custo LP (contínuo): R${self.lp_cost:.4f}\n"
            f"  Custo ILP (inteiro): R${ilp_cost:.2f}\n"
            f"  Gap: {gap_pct:.2f}%\n\n"
            f"PREÇOS SOMBRA:\n"
            f"  Proteína: R${self.shadow_protein:.4f}/g\n"
            f"  Orçamento: R${self.shadow_budget:.4f}/R$\n\n"
            f"CUSTOS REDUZIDOS:\n"
        )
        
        for f, rc in zip(self.foods, self.reduced_costs):
            text += f"  {f.name}: R${rc:.4f}\n"

        self.txt_sens.insert(tk.END, text)