# Diet Protein Optimizer

<p align="center">
  <b>Aplicação desktop em Python para otimização de custo nutricional utilizando Programação Linear Inteira Mista (MILP).</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python" alt="Versão do Python">
  <img src="https://img.shields.io/badge/Licença-MIT-green?style=flat-square" alt="Licença">
  <img src="https://img.shields.io/badge/SciPy-MILP-orange?style=flat-square" alt="SciPy">
</p>

---

## Visão Geral

O **Diet Protein Optimizer** é uma ferramenta educacional e prática desenvolvida em Python para **otimizar a aquisição de alimentos**, focando no objetivo dual de **maximizar a ingestão de proteínas ao menor custo financeiro possível**, respeitando as limitações orçamentais do utilizador.

Combinando rigor matemático e uma interface gráfica fluida, o sistema modela o problema clássico da dieta através de **Programação Linear Inteira (ILP)**, utilizando o solver de última geração **HiGHS** (através da biblioteca `scipy.optimize.milp`). Para fins didáticos, a aplicação também computa a **relaxação contínua (LP)**, explicitando graficamente o impacto do *gap de integralidade* (*integrality gap*) nas decisões reais de compra (unidades inteiras vs. frações).

### O Problema Modelado

O núcleo analítico resolve o seguinte cenário de otimização:

> **Minimizar o custo total financeiro** da cesta de compras, sujeito a:
> - Atender a uma **meta mínima obrigatória de proteína** (em gramas);
> - Respeitar rigidamente um **teto orçamental máximo** (em R$);
> - Restringir o domínio a **quantidades inteiras** (unidades/embalagens discretas, não frações);
> - Garantir, opcionalmente, uma **diversidade mínima de categorias alimentares** para evitar dietas monótonas.

---

## Funcionalidades Principais

| Módulo | Descrição Técnica | Benefício ao Utilizador |
| :--- | :--- | :--- |
| **Cadastro Dinâmico** | Permite a inserção manual de nome, preço, porção unitária e densidade proteica. | Flexibilidade para incluir alimentos locais, sazonais ou suplementos específicos. |
| **Autocomplete Inteligente** | Integração nativa de busca preditiva em bases nutricionais consolidadas (TACO e TBCA). | Agilidade no preenchimento utilizando dados oficiais e fiáveis. |
| **Motor de Otimização MILP** | Resolução do espaço de busca utilizando restrições de integridade via solver HiGHS. | Garantia de soluções ótimas globais exatas (sem frações impraticáveis de alimentos). |
| **Análise de Sensibilidade** | Geração automática de curvas paramétricas Orçamento × Proteína e Fronteiras de Pareto. | Permite compreender o trade-off económico e o impacto marginal de cada unidade monetária investida. |
| **Dualidade e Preços-Sombra** | Cálculo e interpretação económica dos multiplicadores de Lagrange associados. | Traduz o custo marginal oculto para se obter 1g extra de proteína na dieta atual. |
| **Visualização Gráfica** | Renderização 2D interativa do poliedro de restrições (para 2 variáveis) ou gráficos de barras (3+ variáveis). | Facilita o entendimento geométrico do espaço de soluções e da região viável através do Matplotlib. |

---

## Arquitetura do Sistema

O projeto segue princípios de modularidade e separação de conceitos, dividindo-se nos seguintes componentes:

* `main.py`: Ponto de entrada da aplicação. Inicializa o loop de eventos e aplica o tema estético customizado no Tkinter.
* `Protein.py`: Definição do modelo de dados estruturado do alimento (Atributos: preço, gramagem, proteína, categoria).
* `Optimization.py`: O coração do sistema. Contém a rotina de montagem de matrizes esparsas, vetores de restrição e chamadas ao `scipy.optimize.milp`.
* `Window.py`: Subsistema de renderização de janelas secundárias, painéis de formulação matemática e gráficos.
* `dataset_loader.py`: Mecanismo de parsing, indexação e tratamento dos dados TACO/TBCA, contendo atualização monetária corrigida pelo IPCA.

---

## Requisitos e Instalação

### Pré-requisitos
* Python 3.10 ou superior
* Biblioteca gráfica `tkinter` (geralmente distribuída junto ao core do Python)

### Passo a Passo para Instalação

```bash
# 1. Clone o repositório
git clone [https://github.com/seu-usuario/diet-protein-optimizer.git](https://github.com/seu-usuario/diet-protein-optimizer.git)
cd diet-protein-optimizer

# 2. Configure o ambiente virtual isolado (Venv)
python -m venv .venv

# 3. Ative o ambiente virtual
# No Linux/macOS:
source .venv/bin/activate
# No Windows (Prompt de Comando):
.venv\Scripts\activate

# 4. Atualize o gerenciador de pacotes e instale as dependências computacionais
pip install --upgrade pip
pip install numpy scipy matplotlib
