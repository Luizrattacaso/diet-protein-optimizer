import tkinter as tk
from tkinter import ttk
from Protein import Protein

# ============================================================
# FONTES DOS DADOS
# ============================================================
# Valores nutricionais (proteína, gramas/porção):
#   - TACO: Tabela Brasileira de Composição de Alimentos,
#     4ª edição, NEPA/UNICAMP, 2011.
#     Disponível em: https://www.nepa.unicamp.br/taco/
#   - TBCA: Tabela Brasileira de Composição de Alimentos,
#     Versão 7.2, FSP/USP, 2023.
#     Disponível em: https://www.tbca.net.br/
#
# Preços (R$/porção):
#   - Os valores em NUTRITION_DATA são preços de referência
#     com base no ano de publicação do TACO (2011).
#   - Corrigidos automaticamente pelo IPCA acumulado 2011→2026
#     via FATOR_IPCA (≈ ×2,41). Preços finais refletem médias
#     nacionais de alimentos preparados/deli em 2026.
#   - Fonte IPCA: IBGE (2011-2025 oficial; 2026 estimativa
#     acumulada Jan–Mai/2026).
#   - Preços variam por região, estabelecimento e safra.
#
# Formato: (nome, preco_base_2011_R$, gramas_porcao, proteina_g_porcao)
# ============================================================

# ── Correção IPCA 2011 → 2026 ────────────────────────────────────────────────
# Fonte: IBGE — IPCA anual acumulado.
# 2025: valor oficial IBGE. 2026: estimativa acumulada Jan–Mai/2026.
IPCA_ANUAL = {
    2011: 6.50,
    2012: 5.84,
    2013: 5.91,
    2014: 6.41,
    2015: 10.67,
    2016: 6.29,
    2017: 2.95,
    2018: 3.75,
    2019: 4.31,
    2020: 4.52,
    2021: 10.06,
    2022: 5.79,
    2023: 4.62,
    2024: 4.83,
    2025: 5.83,   # IBGE oficial
    2026: 2.68,   # estimativa acumulada Jan–Mai/2026
}

_ANO_BASE  = 2011   # Ano de publicação do TACO — base de referência dos preços
_ANO_ATUAL = 2026


def _calcular_fator_ipca(ano_inicio: int, ano_fim: int) -> float:
    fator = 1.0
    for ano in range(ano_inicio, ano_fim + 1):
        fator *= 1 + IPCA_ANUAL.get(ano, 0.0) / 100
    return round(fator, 6)


FATOR_IPCA = _calcular_fator_ipca(_ANO_BASE, _ANO_ATUAL)
# ─────────────────────────────────────────────────────────────────────────────

NUTRITION_DATA = [
    # ── CARNES BOVINAS ───────────────────────────────────── (19)
    ("Carne bovina - patinho grelhado",          14.00, 100, 26.0),
    ("Carne bovina - alcatra grelhada",          20.00, 100, 27.0),
    ("Carne bovina - coxão mole grelhado",       16.00, 100, 27.5),
    ("Carne bovina - contrafilé grelhado",       22.00, 100, 26.8),
    ("Carne bovina - costela assada",            18.00, 100, 18.0),
    ("Carne bovina - picanha grelhada",          28.00, 100, 28.3),
    ("Carne bovina - fraldinha grelhada",        24.00, 100, 27.6),
    ("Carne bovina - maminha grelhada",          20.00, 100, 28.0),
    ("Carne bovina - músculo cozido",            12.00, 100, 30.1),
    ("Carne bovina - acém cozido",               10.00, 100, 27.5),
    ("Carne bovina - bisteca grelhada",          20.00, 100, 26.8),
    ("Carne bovina - cupim assado",              22.00, 100, 25.5),
    ("Carne bovina - lagarto cozido",            15.00, 100, 28.0),
    ("Carne moída (patinho) refogada",           12.00, 100, 24.0),
    ("Fígado bovino cozido",                     10.00, 100, 29.3),
    ("Coração bovino cozido",                     8.00, 100, 28.7),
    ("Língua bovina cozida",                     12.00, 100, 22.2),
    ("Carne seca cozida",                        18.00, 100, 30.0),
    ("Charque cozido",                           15.00, 100, 25.0),

    # ── AVES ─────────────────────────────────────────────── (14)
    ("Frango - peito grelhado",                   8.50, 100, 31.0),
    ("Frango - coxa assada",                      6.00, 100, 27.5),
    ("Frango - sobrecoxa assada",                 6.50, 100, 26.0),
    ("Frango - asa assada",                       4.50,  80, 19.0),
    ("Frango - sassami grelhado",                 7.00, 100, 31.8),
    ("Frango - fígado refogado",                  6.00, 100, 24.9),
    ("Frango - moela cozida",                     5.00, 100, 26.2),
    ("Frango desfiado cozido",                    8.50, 100, 31.0),
    ("Galinha caipira cozida",                    9.00, 100, 28.0),
    ("Peru - peito assado",                      14.00, 100, 29.0),
    ("Codorna inteira assada",                   15.00, 100, 22.0),
    ("Frango - nuggets assados",                  5.00, 100, 16.0),
    ("Pato - peito assado",                      20.00, 100, 23.5),
    ("Frango - coxinha da asa assada",            5.00, 100, 21.0),

    # ── SUÍNOS E EMBUTIDOS ───────────────────────────────── (20)
    ("Carne de porco - lombo assado",            12.50, 100, 27.0),
    ("Carne de porco - costela assada",          11.00, 100, 19.5),
    ("Carne de porco - pernil assado",           13.00, 100, 27.1),
    ("Carne de porco - paleta cozida",           11.00, 100, 24.0),
    ("Linguiça de frango grelhada",               7.00, 100, 16.0),
    ("Linguiça de porco grelhada",                7.00, 100, 14.0),
    ("Calabresa grelhada",                        7.00, 100, 15.2),
    ("Chouriço cozido",                           8.00, 100, 16.0),
    ("Paio cozido",                               6.00, 100, 13.8),
    ("Joelho de porco cozido",                   15.00, 150, 28.5),
    ("Presunto cozido",                           5.50,  50, 10.2),
    ("Presunto cru (tipo Parma)",                12.00,  50, 13.5),
    ("Peito de peru defumado",                    6.50,  50, 11.5),
    ("Copa defumada",                             9.00,  50, 12.0),
    ("Salame italiano",                           8.00,  50,  9.3),
    ("Pepperoni",                                 8.00,  30,  6.0),
    ("Mortadela",                                 4.50,  50,  7.5),
    ("Salsicha de frango cozida",                 4.00,  50,  7.0),
    ("Bacon defumado",                            6.00,  30,  5.0),
    ("Linguiça calabresa defumada",               6.50, 100, 14.5),

    # ── PEIXES E FRUTOS DO MAR ───────────────────────────── (22)
    ("Salmão grelhado",                          22.00, 100, 25.0),
    ("Tilápia grelhada",                         10.00, 100, 22.0),
    ("Atum em lata (ao natural)",                 5.90,  85, 25.0),
    ("Sardinha em lata",                          4.50,  75, 19.0),
    ("Bacalhau dessalgado cozido",               25.00, 100, 30.6),
    ("Camarão cozido",                           18.00, 100, 20.3),
    ("Saint Peter grelhado",                     12.00, 100, 21.0),
    ("Merluza grelhada",                         11.00, 100, 20.0),
    ("Polvo cozido",                             20.00, 100, 18.0),
    ("Lula grelhada",                            15.00, 100, 17.9),
    ("Corvina grelhada",                         13.00, 100, 22.0),
    ("Robalo grelhado",                          18.00, 100, 23.6),
    ("Dourado (peixe) grelhado",                 16.00, 100, 22.0),
    ("Truta grelhada",                           18.00, 100, 21.5),
    ("Pirarucu assado",                          20.00, 100, 30.2),
    ("Tambaqui grelhado",                        15.00, 100, 23.4),
    ("Pintado grelhado",                         15.00, 100, 22.0),
    ("Mexilhão cozido",                          12.00, 100, 17.9),
    ("Cavala grelhada",                          14.00, 100, 23.0),
    ("Caranguejo cozido",                        18.00, 100, 16.2),
    ("Lagosta cozida",                           35.00, 100, 20.6),
    ("Ostra in natura",                          12.00,  50,  4.8),

    # ── OVOS ─────────────────────────────────────────────── (6)
    ("Ovo inteiro cozido",                        1.20,  50,  6.3),
    ("Ovo inteiro mexido",                        1.50,  60,  7.0),
    ("Clara de ovo pasteurizada",                 2.50, 100, 11.0),
    ("Ovo de codorna cozido (5 un.)",             2.50,  55,  7.2),
    ("Omelete (2 ovos)",                          2.50, 110, 13.7),
    ("Ovo pochê",                                 1.20,  50,  6.3),

    # ── LATICÍNIOS ───────────────────────────────────────── (24)
    ("Leite integral (copo 200ml)",               2.50, 200,  6.6),
    ("Leite desnatado (copo 200ml)",              2.20, 200,  7.0),
    ("Leite UHT semidesnatado (copo 200ml)",      2.30, 200,  6.6),
    ("Leite em pó integral (porção 25g)",         1.80,  25,  5.8),
    ("Iogurte grego natural",                     5.50, 100, 10.0),
    ("Iogurte natural integral",                  3.50, 150,  5.3),
    ("Iogurte proteico",                          6.00, 150, 15.0),
    ("Queijo minas frescal",                      6.00,  50,  7.5),
    ("Queijo cottage",                            8.00, 100, 11.0),
    ("Queijo muçarela",                           8.00,  50, 12.0),
    ("Queijo parmesão ralado",                    7.00,  30,  9.8),
    ("Queijo prato",                              7.00,  50, 12.7),
    ("Queijo provolone",                          8.00,  50, 12.8),
    ("Queijo cheddar",                            7.00,  50, 12.5),
    ("Queijo coalho grelhado",                    6.00,  50, 11.0),
    ("Queijo gouda",                              8.00,  50, 12.5),
    ("Queijo brie",                              10.00,  50, 10.8),
    ("Ricota fresca",                             5.00, 100,  8.0),
    ("Requeijão cremoso",                         4.50,  50,  4.0),
    ("Cream cheese",                              5.00,  50,  3.1),
    ("Coalhada seca",                             5.00, 100, 12.0),
    ("Kefir natural",                             4.00, 200,  7.0),
    ("Bebida láctea fermentada (200ml)",          2.50, 200,  5.2),
    ("Leite de soja (copo 200ml)",                3.50, 200,  7.0),

    # ── SUPLEMENTOS ──────────────────────────────────────── (12)
    ("Whey protein concentrado (dose 30g)",       4.50,  30, 22.0),
    ("Whey protein isolado (dose 30g)",           6.00,  30, 25.0),
    ("Caseína proteica (dose 30g)",               5.50,  30, 23.0),
    ("Albumina em pó (dose 30g)",                 2.50,  30, 24.0),
    ("Proteína vegana de ervilha (dose 30g)",     5.50,  30, 22.0),
    ("Proteína de soja isolada (dose 30g)",       4.50,  30, 25.0),
    ("Proteína de arroz (dose 30g)",              4.00,  30, 20.0),
    ("Proteína de cânhamo (dose 30g)",            6.00,  30, 15.0),
    ("Mix de proteínas blend (dose 30g)",         5.00,  30, 23.0),
    ("Gainer proteico (dose 75g)",                8.00,  75, 30.0),
    ("Barra de proteína",                         7.00,  60, 20.0),
    ("Barra de proteína vegana",                  7.50,  60, 18.0),

    # ── LEGUMINOSAS E DERIVADOS ───────────────────────────── (18)
    ("Feijão carioca cozido",                     2.50, 100,  8.7),
    ("Feijão preto cozido",                       2.50, 100,  8.9),
    ("Feijão fradinho cozido",                    3.00, 100,  8.4),
    ("Feijão azuki cozido",                       4.50, 100,  7.5),
    ("Feijão-de-corda cozido",                    3.00, 100,  7.9),
    ("Feijão branco cozido",                      3.50, 100,  8.1),
    ("Feijão roxinho cozido",                     2.50, 100,  8.8),
    ("Feijão fava cozido",                        3.50, 100,  7.7),
    ("Lentilha cozida",                           4.00, 100,  9.0),
    ("Grão-de-bico cozido",                       5.00, 100,  9.0),
    ("Grão-de-bico tostado (snack)",              6.00,  50,  9.0),
    ("Ervilha cozida",                            4.00, 100,  5.4),
    ("Edamame cozido",                            7.00, 100, 11.9),
    ("Soja em grão cozida",                       3.50, 100, 16.6),
    ("Soja texturizada (PTS) cozida",             3.50, 100, 16.0),
    ("Tofu firme",                                8.00, 100,  8.1),
    ("Tempeh",                                   10.00, 100, 20.3),
    ("Amendoim cru cozido",                       4.50, 100, 13.1),

    # ── OLEAGINOSAS E SEMENTES ────────────────────────────── (17)
    ("Amendoim torrado sem sal",                  5.00, 100, 25.0),
    ("Pasta de amendoim integral",                6.00,  32,  8.0),
    ("Amêndoas cruas",                           15.00,  30,  6.3),
    ("Castanha-do-brasil",                       12.00,  30,  4.1),
    ("Castanha-de-caju torrada",                 14.00,  30,  4.8),
    ("Nozes cruas",                              16.00,  30,  4.5),
    ("Pistache torrado sem sal",                 18.00,  30,  5.8),
    ("Macadâmia torrada",                        20.00,  30,  2.4),
    ("Sementes de abóbora torradas",              8.00,  30,  8.8),
    ("Sementes de girassol torradas",             6.00,  30,  6.1),
    ("Sementes de chia",                          4.50,  30,  4.7),
    ("Gergelim torrado",                          4.00,  30,  6.1),
    ("Tahine (pasta de gergelim)",                5.00,  30,  5.4),
    ("Linhaça dourada",                           3.00,  30,  5.2),
    ("Sementes de cânhamo",                       8.00,  30,  9.5),
    ("Farinha de amêndoas",                      10.00,  50, 10.6),
    ("Noz-pecã torrada",                         18.00,  30,  2.9),

    # ── CEREAIS, GRÃOS E PANIFICAÇÃO ─────────────────────── (21)
    ("Quinoa cozida",                             7.00, 100,  4.4),
    ("Amaranto cozido",                           6.00, 100,  3.8),
    ("Trigo sarraceno cozido",                    5.00, 100,  4.5),
    ("Cevada pérola cozida",                      3.50, 100,  2.7),
    ("Cuscuz marroquino cozido",                  4.00, 100,  3.8),
    ("Aveia em flocos",                           3.00,  80, 11.2),
    ("Granola proteica (sem açúcar)",             5.00,  50,  8.0),
    ("Gérmen de trigo",                           3.00,  30,  9.0),
    ("Arroz integral cozido",                     2.00, 100,  2.6),
    ("Arroz branco cozido",                       1.80, 100,  2.5),
    ("Macarrão integral cozido",                  3.50, 100,  5.8),
    ("Espaguete cozido",                          3.00, 100,  4.5),
    ("Massa de lentilha cozida",                  4.50, 100,  9.0),
    ("Farinha de grão-de-bico (50g)",             4.00,  50,  9.5),
    ("Farinha de soja (50g)",                     3.00,  50, 22.0),
    ("Pão integral (fatia 50g)",                  2.50,  50,  4.0),
    ("Pão de forma branco (fatia 50g)",           2.00,  50,  3.3),
    ("Cogumelo shitake refogado",                 9.00, 100,  2.2),
    ("Cogumelo champignon refogado",              7.00, 100,  3.3),
    ("Cogumelo portobello grelhado",              8.00, 100,  4.0),
    ("Tapioca (200g)",                            4.00, 200,  0.7),

    # ── VEGETAIS COM PROTEÍNA ─────────────────────────────── (16)
    ("Brócolis cozido",                           2.50, 100,  3.5),
    ("Couve-flor cozida",                         2.50, 100,  2.4),
    ("Espinafre cozido",                          3.50, 100,  3.0),
    ("Couve manteiga refogada",                   3.00, 100,  3.0),
    ("Couve-de-bruxelas cozida",                  6.00, 100,  3.4),
    ("Aspargo cozido",                            5.00, 100,  3.0),
    ("Alcachofra cozida",                         5.00, 100,  3.5),
    ("Milho verde cozido",                        2.50, 100,  3.2),
    ("Ervilha fresca cozida",                     4.50, 100,  6.9),
    ("Feijão-vagem cozido",                       3.50, 100,  1.8),
    ("Quiabo cozido",                             3.50, 100,  2.1),
    ("Abobrinha refogada",                        3.00, 100,  1.5),
    ("Palmito de pupunha em conserva",            4.50, 100,  3.5),
    ("Batata-doce assada",                        3.50, 100,  1.8),
    ("Beterraba cozida",                          3.00, 100,  1.7),
    ("Mandioca cozida",                           2.50, 100,  1.3),

    # ── ALIMENTOS FUNCIONAIS E ESPECIAIS ─────────────────── (14)
    ("Seitan (glúten de trigo cozido)",           8.00, 100, 25.0),
    ("Tempeh de grão-de-bico",                   11.00, 100, 18.0),
    ("Natto (soja fermentada)",                  12.00, 100, 16.0),
    ("Tofu sedoso",                               7.00, 100,  5.0),
    ("Missô (pasta de soja fermentada)",          4.00,  30,  4.2),
    ("Spirulina em pó (10g)",                     8.00,  10,  5.5),
    ("Levedo de cerveja (20g)",                   3.00,  20,  8.0),
    ("Levedo nutricional (15g)",                  6.00,  15,  8.3),
    ("Farinha de soja desengordurada (50g)",      3.50,  50, 24.5),
    ("Proteína texturizada de ervilha (50g)",     5.00,  50, 20.0),
    ("Feijão mungo cozido",                       3.50, 100,  7.0),
    ("Proteína de feijão em pó (dose 30g)",       4.00,  30, 22.0),
    ("Quinoa em flocos (50g)",                    7.00,  50,  4.5),
    ("Amaranto em flocos (50g)",                  6.00,  50,  3.8),
]


def _por_kg(nome, preco, gramas, proteina):
    """Normaliza para 1000g (1kg): só escala proteína. Preço mantido como referência base TACO."""
    if gramas == 1000:
        return nome, preco, 1000, proteina
    f = 1000.0 / gramas
    return nome, preco, 1000, round(proteina * f, 2)


def get_all_foods():
    return [Protein(n, round(p * FATOR_IPCA, 2), g, pr)
            for n, p, g, pr in (_por_kg(*x) for x in NUTRITION_DATA)]


def search_foods(query: str):
    q = query.lower()
    return [Protein(n, round(p * FATOR_IPCA, 2), g, pr)
            for n, p, g, pr in (_por_kg(*x) for x in NUTRITION_DATA)
            if q in n.lower()]


class DatasetDialog(tk.Toplevel):
    def __init__(self, parent, on_add_callback):
        super().__init__(parent)
        self.title("Dataset de Alimentos — TACO/TBCA (UNICAMP/USP)")
        self.geometry("620x520")
        self.resizable(False, False)
        self._on_add = on_add_callback
        self._all = get_all_foods()
        self._displayed = list(self._all)
        self._setup_ui()
        self.grab_set()

    def _setup_ui(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 4))
        top.pack(fill="x")
        ttk.Label(top, text="Buscar:").pack(side="left")
        self._ent = ttk.Entry(top, width=30)
        self._ent.pack(side="left", padx=6)
        self._ent.bind("<KeyRelease>", self._filter)
        ttk.Label(top, text="(Ctrl+A = todos  |  Ctrl+Clique = múltiplos)", font=("Segoe UI", 8)).pack(side="left")

        info = ttk.Frame(self, padding=(12, 0, 12, 2))
        info.pack(fill="x")
        ttk.Label(
            info,
            text="Fonte nutricional: TACO 4ª ed. (UNICAMP/NEPA, 2011) + TBCA 7.2 (FSP/USP, 2023) | Preços: estimativas IPCA/IBGE e IPC/FIPE 2024-2025",
            font=("Segoe UI", 7),
            foreground="#666666",
        ).pack(anchor="w")

        mid = ttk.Frame(self, padding=(12, 2, 12, 4))
        mid.pack(fill="both", expand=True)
        ttk.Label(mid, text="  Nome do Alimento                                            R$/porção   Prot/porção").pack(anchor="w")

        lb_wrap = tk.Frame(mid, highlightthickness=1, highlightbackground="#CBD5E0", bg="#fff")
        lb_wrap.pack(fill="both", expand=True)
        lb_wrap.grid_columnconfigure(0, weight=1)

        self._lb = tk.Listbox(
            lb_wrap, selectmode="extended", font=("Consolas", 9),
            bg="#FFFFFF", fg="#1A237E", selectbackground="#1565C0",
            selectforeground="white", borderwidth=0, activestyle="none",
            exportselection=False,
        )
        self._lb.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(lb_wrap, orient="vertical", command=self._lb.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self._lb.configure(yscrollcommand=sb.set)
        lb_wrap.grid_rowconfigure(0, weight=1)

        self._populate(self._all)

        bot = ttk.Frame(self, padding=(12, 6, 12, 12))
        bot.pack(fill="x")
        self._lbl_count = ttk.Label(bot, text=f"{len(self._all)} alimentos", font=("Segoe UI", 8), foreground="#555")
        self._lbl_count.pack(side="left", padx=(0, 10))
        ttk.Button(bot, text="✅ Adicionar Selecionados", command=self._add).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ttk.Button(bot, text="Fechar", command=self.destroy).pack(side="left", fill="x", expand=True)

    def _populate(self, foods):
        self._lb.delete(0, tk.END)
        self._displayed = foods
        for f in foods:
            self._lb.insert(
                tk.END,
                f"  {f.name:<50}  R${f.price:>5.2f}   {f.protein_grams:>5.1f}g",
            )
        if hasattr(self, "_lbl_count"):
            self._lbl_count.config(text=f"{len(foods)} alimento(s)")

    def _filter(self, _=None):
        q = self._ent.get().strip()
        self._populate(search_foods(q) if q else self._all)

    def _add(self):
        for i in self._lb.curselection():
            self._on_add(self._displayed[i])
        self.destroy()
