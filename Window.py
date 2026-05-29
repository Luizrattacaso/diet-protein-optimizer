import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon
from scipy.optimize import milp, LinearConstraint, Bounds

class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, foods, x_opt, target_prot, budget, x_lp=None):
        super().__init__(parent)
        self.title("Resultado - Resolução Gráfica")
        self.geometry("1100x900")

        self.foods = foods
        self.x_opt = x_opt
        self.x_lp = x_lp
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

        math_text += f"\nCusto ILP: R${total_cost:.2f} | Proteína: {total_prot:.1f}g"

        if self.x_lp is not None:
            math_text += f"\n\nLP RELAXADO (solução contínua / fracionária):\n"
            total_cost_lp = total_prot_lp = 0
            for f, val in zip(self.foods, self.x_lp):
                cost_item = val * f.price
                prot_item = val * f.protein_grams
                total_cost_lp += cost_item
                total_prot_lp += prot_item
                math_text += f"  • {f.name}: x = {val:.3f} un. | Custo: R${cost_item:.2f} | Prot: {prot_item:.1f}g\n"
            gap = (total_cost - total_cost_lp) / total_cost_lp * 100 if total_cost_lp > 0 else 0
            math_text += f"\nCusto LP: R${total_cost_lp:.2f} | Proteína LP: {total_prot_lp:.1f}g"
            math_text += f"\nGap de Integralidade: {gap:.2f}%  [ (Z_ILP - Z_LP) / Z_LP ]"

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
                    label=f'Ponto Ótimo ILP\n({opt_x1:.0f}, {opt_x2:.0f})', zorder=5)

        Z_opt = f1.price * opt_x1 + f2.price * opt_x2
        if f2.price != 0:
            x2_obj = (Z_opt - f1.price * x1) / f2.price
            self.ax.plot(x1, x2_obj, 'g--', linewidth=1.5, alpha=0.8,
                        label=f'F.O. ILP (Z = R${Z_opt:.2f})')

        if self.x_lp is not None and len(self.x_lp) >= 2:
            lp_x1, lp_x2 = self.x_lp[0], self.x_lp[1]
            Z_lp = f1.price * lp_x1 + f2.price * lp_x2
            self.ax.plot(lp_x1, lp_x2, 'bD', markersize=14, markeredgewidth=2,
                        markeredgecolor='darkblue',
                        label=f'Ponto Ótimo LP\n({lp_x1:.2f}, {lp_x2:.2f})', zorder=4)
            if f2.price != 0:
                x2_obj_lp = (Z_lp - f1.price * x1) / f2.price
                self.ax.plot(x1, x2_obj_lp, 'b:', linewidth=1.5, alpha=0.7,
                            label=f'F.O. LP (Z = R${Z_lp:.2f})')

        self.ax.set_xlabel(f'Quantidade: {f1.name} (x₁)', fontsize=11, fontweight='bold')
        self.ax.set_ylabel(f'Quantidade: {f2.name} (x₂)', fontsize=11, fontweight='bold')
        self.ax.set_title('RESOLUÇÃO GRÁFICA: Linhas Delimitam o Espaço de Soluções',
                         fontsize=13, fontweight='bold', pad=15)
        self.ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
        self.ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.8)
        self.ax.set_xlim(0, max_x1)
        self.ax.set_ylim(0, max_x2)

        total_prot = f1.protein_grams*opt_x1 + f2.protein_grams*opt_x2
        info = (f'ILP (inteiro)\n'
                f'x₁={opt_x1:.0f}  x₂={opt_x2:.0f}\n'
                f'Custo: R${Z_opt:.2f}\n'
                f'Proteína: {total_prot:.1f}g')
        if self.x_lp is not None and len(self.x_lp) >= 2:
            lp_x1_v, lp_x2_v = self.x_lp[0], self.x_lp[1]
            Z_lp_v = f1.price * lp_x1_v + f2.price * lp_x2_v
            gap = (Z_opt - Z_lp_v) / Z_lp_v * 100 if Z_lp_v > 0 else 0
            info += (f'\n━━━━━━━━━━━━\n'
                    f'LP (fracionário)\n'
                    f'x₁={lp_x1_v:.2f}  x₂={lp_x2_v:.2f}\n'
                    f'Custo: R${Z_lp_v:.2f}\n'
                    f'Gap: {gap:.2f}%')
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

        quantities_ilp = [self.x_opt[i] for i in range(len(names))]
        costs_ilp = [f.price * self.x_opt[i] for i, f in enumerate(self.foods)]
        proteins_ilp = [f.protein_grams * self.x_opt[i] for i, f in enumerate(self.foods)]

        if self.x_lp is not None:
            self.fig.clear()
            ax1 = self.fig.add_subplot(2, 1, 1)
            ax2 = self.fig.add_subplot(2, 1, 2)

            quantities_lp = [self.x_lp[i] for i in range(len(names))]
            width = 0.35
            ax1.bar(x_pos - width / 2, quantities_lp, width, label='LP (fracionário)',
                    color='#81C784', alpha=0.85, hatch='//')
            ax1.bar(x_pos + width / 2, quantities_ilp, width, label='ILP (inteiro)',
                    color='#4CAF50')
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(names, rotation=15, ha='right', fontsize=8)
            ax1.set_ylabel('Quantidade')
            ax1.set_title('Quantidade por Alimento — LP vs ILP')
            ax1.legend(fontsize=9)
            ax1.grid(axis='y', alpha=0.3)

            total_cost_lp = sum(f.price * self.x_lp[i] for i, f in enumerate(self.foods))
            total_prot_lp = sum(f.protein_grams * self.x_lp[i] for i, f in enumerate(self.foods))
            total_cost_ilp = sum(costs_ilp)
            total_prot_ilp = sum(proteins_ilp)
            gap = (total_cost_ilp - total_cost_lp) / total_cost_lp * 100 if total_cost_lp > 0 else 0

            cats = ['Custo Total (R$)', 'Proteína Total (g)']
            lp_vals = [total_cost_lp, total_prot_lp]
            ilp_vals = [total_cost_ilp, total_prot_ilp]
            x2 = np.arange(2)
            ax2.bar(x2 - 0.2, lp_vals, 0.35, label='LP', color='#2196F3', alpha=0.85, hatch='//')
            ax2.bar(x2 + 0.2, ilp_vals, 0.35, label='ILP', color='#1565C0')
            ax2.set_xticks(x2)
            ax2.set_xticklabels(cats)
            ax2.legend(fontsize=9)
            ax2.set_title(f'Totais — LP vs ILP  |  Gap de Integralidade: {gap:.2f}%')
            ax2.grid(axis='y', alpha=0.3)
            for i, (lp_v, ilp_v) in enumerate(zip(lp_vals, ilp_vals)):
                ax2.text(i - 0.2, lp_v * 1.02, f'{lp_v:.1f}', ha='center', fontsize=8)
                ax2.text(i + 0.2, ilp_v * 1.02, f'{ilp_v:.1f}', ha='center', fontsize=8)
        else:
            width = 0.25
            self.ax.bar(x_pos - width, quantities_ilp, width, label='Qtd', color='#4CAF50')
            self.ax.bar(x_pos, costs_ilp, width, label='Custo (R$)', color='#2196F3')
            self.ax.bar(x_pos + width, proteins_ilp, width, label='Proteína (g)', color='#FF9800')
            self.ax.set_xticks(x_pos)
            self.ax.set_xticklabels(names, rotation=15, ha='right')
            self.ax.set_ylabel('Valor')
            self.ax.set_title('Distribuição da Solução Ótima')
            self.ax.legend()
            self.ax.grid(axis='y', alpha=0.3)
            self.ax.axhline(y=self.budget, color='red', linestyle=':', alpha=0.6, label='Limite Orçamento')
            self.ax.axhline(y=self.target_prot, color='purple', linestyle=':', alpha=0.6, label='Meta Proteína')


class SensitivityWindow(tk.Toplevel):
    def __init__(self, parent, foods, target_prot, budget):
        super().__init__(parent)
        self.title("Análise de Sensibilidade — Fronteira de Pareto")
        self.geometry("1200x720")

        self.foods = foods
        self.target_prot = target_prot
        self.budget = budget

        self._setup_ui()
        self.after(60, self._run_and_plot)

    def _setup_ui(self):
        info_frame = ttk.LabelFrame(self, text="5. Análise de Sensibilidade", padding=10)
        info_frame.pack(fill="x", padx=20, pady=(10, 5))
        self.lbl_info = ttk.Label(info_frame,
            text="Calculando curvas de sensibilidade...", font=("Consolas", 9))
        self.lbl_info.pack(fill="x")

        graph_frame = ttk.LabelFrame(self,
            text="Orçamento × Proteína Alcançável  /  Fronteira de Pareto — Custo × Meta",
            padding=10)
        graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(13, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _run_and_plot(self):
        n = len(self.foods)
        c_cost     = np.array([f.price          for f in self.foods])
        c_prot_neg = np.array([-f.protein_grams for f in self.foods])

        # ── Varredura de orçamento: maximizar proteína para cada budget ───────
        budget_max = max(self.budget * 3, 100)
        b_budgets, b_prots = [], []
        for b in np.arange(10, budget_max + 1, 10):
            A = np.array([[f.price for f in self.foods]], dtype=float)
            res = milp(c_prot_neg,
                       constraints=LinearConstraint(A, lb=[-np.inf], ub=[float(b)]),
                       integrality=np.ones(n), bounds=Bounds(lb=0))
            if res.success:
                x = np.maximum(np.round(res.x), 0)
                b_budgets.append(float(b))
                b_prots.append(float(sum(f.protein_grams * x[i]
                                         for i, f in enumerate(self.foods))))

        # ── Pareto: minimizar custo para cada meta de proteína (sem limite) ───
        prot_max = max(self.target_prot * 3, 100)
        p_targets, p_costs = [], []
        for p in np.arange(10, prot_max + 1, 10):
            A = np.array([[f.protein_grams for f in self.foods]], dtype=float)
            res = milp(c_cost,
                       constraints=LinearConstraint(A, lb=[float(p)], ub=[np.inf]),
                       integrality=np.ones(n), bounds=Bounds(lb=0))
            if res.success:
                x = np.maximum(np.round(res.x), 0)
                p_targets.append(float(p))
                p_costs.append(float(c_cost @ x))

        self._plot(b_budgets, b_prots, p_targets, p_costs)

    def _plot(self, b_budgets, b_prots, p_targets, p_costs):
        # ── Subplot 1: Orçamento × Proteína Máxima ───────────────────────────
        ax1 = self.ax1
        ax1.clear()
        if b_budgets:
            ax1.step(b_budgets, b_prots, where='post',
                     color='#1565C0', linewidth=2.5, label='Proteína máxima (g)')
            ax1.fill_between(b_budgets, b_prots, step='post',
                             alpha=0.12, color='#1565C0')
            ax1.axhline(y=self.target_prot, color='red', linestyle='--',
                        linewidth=1.8, label=f'Meta: {self.target_prot:.0f}g')
            ax1.axvline(x=self.budget, color='#E65100', linestyle='--',
                        linewidth=1.8, label=f'Orçamento atual: R${self.budget:.0f}')

            feasible = [(b, p) for b, p in zip(b_budgets, b_prots)
                        if p >= self.target_prot]
            if feasible:
                min_b = feasible[0][0]
                span = b_budgets[-1] - b_budgets[0]
                ax1.annotate(
                    f'Mín. para meta:\nR${min_b:.0f}',
                    xy=(min_b, self.target_prot),
                    xytext=(min_b + span * 0.12, self.target_prot * 0.78),
                    arrowprops=dict(arrowstyle='->', color='darkred', lw=1.4),
                    fontsize=8, color='darkred',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFEBEE', alpha=0.85))

        ax1.set_xlabel('Orçamento (R$)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Proteína máxima alcançável (g)', fontsize=11, fontweight='bold')
        ax1.set_title('Variação do Orçamento\n(degraus = arredondamento ILP)',
                      fontsize=11, fontweight='bold')
        ax1.legend(fontsize=9, framealpha=0.9)
        ax1.grid(True, alpha=0.3, linestyle=':')

        # ── Subplot 2: Fronteira de Pareto ────────────────────────────────────
        ax2 = self.ax2
        ax2.clear()
        if p_targets:
            ax2.step(p_targets, p_costs, where='post',
                     color='#C62828', linewidth=2.5, label='Custo mínimo (R$)')
            ax2.fill_between(p_targets, p_costs, step='post',
                             alpha=0.12, color='#C62828')
            ax2.axvline(x=self.target_prot, color='blue', linestyle='--',
                        linewidth=1.8, label=f'Meta atual: {self.target_prot:.0f}g')
            ax2.axhline(y=self.budget, color='#E65100', linestyle='--',
                        linewidth=1.8, label=f'Orçamento: R${self.budget:.0f}')

        ax2.set_xlabel('Meta de Proteína (g)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Custo mínimo (R$)', fontsize=11, fontweight='bold')
        ax2.set_title('Fronteira de Pareto — Custo × Meta de Proteína\n'
                      '(sem restrição de orçamento)',
                      fontsize=11, fontweight='bold')
        ax2.legend(fontsize=9, framealpha=0.9)
        ax2.grid(True, alpha=0.3, linestyle=':')

        self.fig.tight_layout(pad=2.5)
        self.canvas.draw()

        # ── Resumo informativo ────────────────────────────────────────────────
        parts = []
        if b_budgets:
            feasible = [(b, p) for b, p in zip(b_budgets, b_prots)
                        if p >= self.target_prot]
            if feasible:
                parts.append(f"Orçamento mínimo para {self.target_prot:.0f}g: R${feasible[0][0]:.0f}")
            idx = min(range(len(b_budgets)), key=lambda i: abs(b_budgets[i] - self.budget))
            parts.append(f"Com R${self.budget:.0f}: até {b_prots[idx]:.0f}g de proteína")
        if p_targets:
            parts.append(
                f"Pareto: {len(p_targets)} pontos "
                f"({p_targets[0]:.0f}g–{p_targets[-1]:.0f}g)")
        self.lbl_info.config(
            text="   |   ".join(parts) if parts else "Análise concluída.")
