import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon

class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, foods, x_opt, target_prot, budget):
        super().__init__(parent)
        self.title("Resultado - Resolução Gráfica")
        self.geometry("1100x900")
        
        self.foods = foods
        self.x_opt = x_opt
        self.target_prot = target_prot
        self.budget = budget
        
        self._setup_ui()
        self._display_math()
        self._plot_graph()

    def _setup_ui(self):
        res_frame = ttk.LabelFrame(self, text="3. Formulação e Resultados", padding=15)
        res_frame.pack(fill="x", padx=20, pady=10)
        self.txt_math = tk.Text(res_frame, height=8, wrap=tk.WORD, font=("Consolas", 10))
        self.txt_math.pack(fill="both", expand=True)

        graph_frame = ttk.LabelFrame(self, text="4. Espaço de Soluções (Região Viável)", padding=15)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _display_math(self):
        c = [f.price for f in self.foods]
        vars_str = f"x_i = quantidade do alimento {', '.join([f.name for f in self.foods])}"
        obj_str = "Min Z = " + " + ".join([f"{f.price}·x_{i+1}" for i, f in enumerate(self.foods)])
        constr_prot = " + ".join([f"{f.protein_grams}·x_{i+1}" for i, f in enumerate(self.foods)])
        constr_budget = " + ".join([f"{f.price}·x_{i+1}" for i, f in enumerate(self.foods)])
        
        math_text = (
            f"MODELO DE PROGRAMAÇÃO LINEAR\n{'='*50}\n"
            f"Variáveis: {vars_str}\n\n"
            f"Função Objetivo:\n  {obj_str}\n\n"
            f"Restrições (Espaço de Possibilidades):\n"
            f"{constr_prot} ≥ {self.target_prot}  (Proteína mínima)\n"
            f"{constr_budget} ≤ {self.budget}  (Orçamento máximo)\n"
            f" x_i ≥ 0  (Não-negatividade)\n\n"
            f"SOLUÇÃO ÓTIMA:\n"
        )
        
        total_cost = total_prot = 0
        for f, val in zip(self.foods, self.x_opt):
            cost_item = val * f.price
            prot_item = val * f.protein_grams
            total_cost += cost_item
            total_prot += prot_item
            math_text += f"  • {f.name}: x = {int(val)} un. | Custo: R${cost_item:.2f} | Prot: {prot_item:.1f}g\n"
        
        math_text += f"\nCusto Total: R${total_cost:.2f}\nProteína Total: {total_prot:.1f}g"
        self.txt_math.insert(tk.END, math_text)

    def _plot_graph(self):
        self.ax.clear()
        
        if len(self.foods) == 2:
            self._plot_2d_feasible_region()
        else:
            self._plot_multi_bars()
        
        self.fig.tight_layout()
        self.canvas.draw()

    def _plot_2d_feasible_region(self):
        f1, f2 = self.foods[0], self.foods[1]
        
        max_x1 = max(
            self.budget / f1.price * 1.3 if f1.price > 0 else 10,
            self.target_prot / f1.protein_grams * 1.3 if f1.protein_grams > 0 else 10
        )
        max_x2 = max(
            self.budget / f2.price * 1.3 if f2.price > 0 else 10,
            self.target_prot / f2.protein_grams * 1.3 if f2.protein_grams > 0 else 10
        )
        
        x1 = np.linspace(0, max_x1, 200)
        
        if f2.protein_grams != 0:
            x2_prot = (self.target_prot - f1.protein_grams * x1) / f2.protein_grams
        else:
            x2_prot = np.full_like(x1, -np.inf)

        if f2.price != 0:
            x2_budget = (self.budget - f1.price * x1) / f2.price
        else:
            x2_budget = np.full_like(x1, np.inf)
        
        self.ax.plot(x1, x2_prot, 'r-', linewidth=2.5, label=f'Limite: Proteína ≥ {self.target_prot}g')
        self.ax.plot(x1, x2_budget, 'b-', linewidth=2.5, label=f'Limite: Orçamento ≤ R${self.budget}')
        
        self.ax.axhline(y=0, color='k', linewidth=1.5)
        self.ax.axvline(x=0, color='k', linewidth=1.5)
        
        vertices = self._find_feasible_polygon(f1, f2, max_x1, max_x2)
        if len(vertices) >= 3:
            region = Polygon(vertices, color='yellow', alpha=0.4, label='Espaço de Possibilidades (Viável)')
            self.ax.add_patch(region)
            verts_arr = np.array(vertices)
            self.ax.plot(verts_arr[:, 0], verts_arr[:, 1], 'ko', markersize=5, alpha=0.7)
        
        opt_x1, opt_x2 = self.x_opt[0], self.x_opt[1]
        self.ax.plot(opt_x1, opt_x2, 'r*', markersize=20, markeredgewidth=2.5, 
                    label=f'Ponto Ótimo\n({opt_x1:.0f}, {opt_x2:.0f})', zorder=5)
        
        Z_opt = f1.price * opt_x1 + f2.price * opt_x2
        if f2.price != 0:
            x2_obj = (Z_opt - f1.price * x1) / f2.price
            self.ax.plot(x1, x2_obj, 'g--', linewidth=1.5, alpha=0.8, 
                        label=f'Função Objetivo\n(Z = R${Z_opt:.2f})')
        
        self.ax.set_xlabel(f'Quantidade: {f1.name} (x₁)', fontsize=11, fontweight='bold')
        self.ax.set_ylabel(f'Quantidade: {f2.name} (x₂)', fontsize=11, fontweight='bold')
        self.ax.set_title('RESOLUÇÃO GRÁFICA: Linhas Delimitam o Espaço de Soluções', 
                         fontsize=13, fontweight='bold', pad=15)
        self.ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        self.ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
        self.ax.set_xlim(0, max_x1)
        self.ax.set_ylim(0, max_x2)
        
        total_prot = f1.protein_grams*opt_x1 + f2.protein_grams*opt_x2
        info = (f'SOLUÇÃO ÓTIMA\n'
                f'x₁ = {opt_x1:.0f} ({f1.name})\n'
                f'x₂ = {opt_x2:.0f} ({f2.name})\n'
                f'━━━━━━━━━━━━━━\n'
                f'Custo: R${Z_opt:.2f}\n'
                f'Proteína: {total_prot:.1f}g')
        self.ax.text(0.02, 0.98, info, transform=self.ax.transAxes, fontsize=10, 
                    verticalalignment='top', fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                             edgecolor='black', linewidth=1.5))

    def _find_feasible_polygon(self, f1, f2, max_x1, max_x2):
        vertices = []
        
        det = f1.protein_grams * f2.price - f2.protein_grams * f1.price
        if abs(det) > 1e-10:
            x1_int = (self.target_prot * f2.price - self.budget * f2.protein_grams) / det
            x2_int = (self.budget * f1.protein_grams - self.target_prot * f1.price) / det
            if 0 <= x1_int <= max_x1 and 0 <= x2_int <= max_x2:
                vertices.append((x1_int, x2_int))
        
        candidates = []
        
        if f1.protein_grams > 0:
            candidates.append((self.target_prot / f1.protein_grams, 0))
        if f1.price > 0:
            candidates.append((self.budget / f1.price, 0))
        
        if f2.protein_grams > 0:
            candidates.append((0, self.target_prot / f2.protein_grams))
        if f2.price > 0:
            candidates.append((0, self.budget / f2.price))
        
        for x1_c, x2_c in candidates:
            if x1_c < 0 or x2_c < 0 or x1_c > max_x1 or x2_c > max_x2:
                continue
            prot_ok = f1.protein_grams*x1_c + f2.protein_grams*x2_c >= self.target_prot - 1e-6
            budget_ok = f1.price*x1_c + f2.price*x2_c <= self.budget + 1e-6
            if prot_ok and budget_ok:
                vertices.append((x1_c, x2_c))

        if len(vertices) >= 3:
            center = (sum(v[0] for v in vertices)/len(vertices), 
                     sum(v[1] for v in vertices)/len(vertices))
            vertices.sort(key=lambda v: np.arctan2(v[1]-center[1], v[0]-center[0]))
        
        return vertices

    def _plot_multi_bars(self):
        names = [f.name for f in self.foods]
        x_pos = np.arange(len(names))
        width = 0.25
        
        quantities = [self.x_opt[i] for i in range(len(names))]
        costs = [f.price * self.x_opt[i] for i, f in enumerate(self.foods)]
        proteins = [f.protein_grams * self.x_opt[i] for i, f in enumerate(self.foods)]
        
        self.ax.bar(x_pos - width, quantities, width, label='Qtd', color='#4CAF50')
        self.ax.bar(x_pos, costs, width, label='Custo (R$)', color='#2196F3')
        self.ax.bar(x_pos + width, proteins, width, label='Proteína (g)', color='#FF9800')
        
        self.ax.set_xticks(x_pos)
        self.ax.set_xticklabels(names, rotation=15, ha='right')
        self.ax.set_ylabel('Valor')
        self.ax.set_title('Distribuição da Solução Ótima')
        self.ax.legend()
        self.ax.grid(axis='y', alpha=0.3)
        
        self.ax.axhline(y=self.budget, color='red', linestyle=':', alpha=0.6, label='Limite Orçamento')
        self.ax.axhline(y=self.target_prot, color='purple', linestyle=':', alpha=0.6, label='Meta Proteína')