#!/usr/bin/env -S .venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def plot_grafico_linha(df_plot, metric_col, y_label, titulo, arq_saida, add_hours_suffix=False):
    """Gera e salva um gráfico de linha para a métrica especificada."""
    
    # Cria uma nova figura para cada gráfico
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    # --- Formatação do Eixo Y (Adicionar 'h' nas horas) ---
    if add_hours_suffix:
        def hours_formatter(x, pos):
            # Formata o valor com uma casa decimal e adiciona o ' h'
            return f'{x:.1f} h'
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(hours_formatter))

    particoes = df_plot['particao'].unique()
    
    # Configuração de cores
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    color_cycle = plt.cycler(color=colors)
    plt.gca().set_prop_cycle(color_cycle)

    for particao in particoes:
        # Filtra e garante a ordenação por data
        subset = df_plot[df_plot['particao'] == particao].sort_values(by='data_mensal')
        
        if not subset.empty:
            plt.plot(
                subset['data_mensal'],
                subset[metric_col],
                marker='o',
                linestyle='-',
                linewidth=2,
                markersize=5,
                label=particao
            )

    # Configurações do gráfico
    plt.title(titulo, fontsize=16, y=1.2)
    plt.xlabel('Ano-Mês', fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Configurar ticks do eixo X
    x_labels = df_plot['data_mensal'].unique()
    if len(x_labels) > 15:
        step = int(np.ceil(len(x_labels) / 15))
        plt.xticks(x_labels[::step], rotation=45, ha='right')
    else:
        plt.xticks(x_labels, rotation=45, ha='right')
        
    # Posiciona a legenda fora do gráfico
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), 
               ncol=len(particoes) // 2 + 1, fontsize=10)

    plt.tight_layout()
    plt.savefig(f"graficos/{arq_saida}")
    print(f"Gráfico '{titulo}' salvo como '{arq_saida}'.")
    plt.close() # Fecha a figura

# Simplificar os nomes dos centros
def simplificar_nome(nome):
    if ' - ' in nome:
        return nome.split(' - ')[-1].replace('.', '')
    
def plot_grafico_pizza(df_plot, cores, arq_saida):
    """Gera e salva um gráfico de pizza para a distribuição de usuários por centro."""
    
    # Preparação dos Dados Comuns de Usuários por Centro
    contagem_centro = df_plot['centro'].value_counts()
    contagem_centro_simplificado = contagem_centro.copy()
    contagem_centro_simplificado.index = contagem_centro_simplificado.index.map(simplificar_nome)

    # Agrupar categorias pequenas em "Outros"
    outras_contagens = contagem_centro_simplificado[contagem_centro_simplificado <= 5].sum()

    # Capturar nomes e contagens AGRUPADAS para detalhamento na legenda
    centros_pequenos = contagem_centro_simplificado[contagem_centro_simplificado <= 5].sort_values(ascending=False)
    nomes_detalhados_list = [f"{name} ({count})" for name, count in centros_pequenos.items()]
    nomes_detalhados_str = ", ".join(nomes_detalhados_list)

    if outras_contagens > 0:
        contagem_final = contagem_centro_simplificado[contagem_centro_simplificado > 5].copy()
        contagem_final['Outros'] = outras_contagens
    else:
        contagem_final = contagem_centro_simplificado.copy()

    contagem_final = contagem_final.sort_values(ascending=False)
    total_usuarios = contagem_final.sum()

    plt.figure(figsize=(15, 10))
    ax = plt.gca()

    wedges, texts = ax.pie(
        contagem_final.values,
        labels=None,
        autopct=None,
        startangle=90,
        wedgeprops={'edgecolor': 'black', 'linewidth': 1},
        colors=cores
    )

    # Colocar os rótulos de dados (Contagem e Porcentagem) fora das fatias
    OUTER_RADIUS = 1.1 # Controla a distância dos rótulos à borda da pizza

    for i, (wedge, value) in enumerate(zip(wedges, contagem_final.values)):
        # Calcular o ângulo central
        ang = (wedge.theta2 - wedge.theta1) / 2. + wedge.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]

        # Posição final (Raio*X, Raio*Y)
        ax.text(OUTER_RADIUS * x, OUTER_RADIUS * y,
                f"{value}\n({value/total_usuarios*100:.1f}%)",
                ha=horizontalalignment,
                va="center",
                fontsize=10,
                color='black'
        )

    # Configurar a legenda em um bloco separado à direita
    # Monta a legenda com o detalhamento de 'Outros'
    legend_labels = []
    for label, value in contagem_final.items():
        if label == 'Outros':
            # Adiciona a lista de centros agrupados com suas contagens
            legend_labels.append(f"{label} ({value}) - Centros: {nomes_detalhados_str}")
        else:
            legend_labels.append(f"{label} ({value})")

    ax.legend(
        wedges,
        legend_labels,
        title="Centros (Usuários)",
        loc="center left",
        bbox_to_anchor=(1, 0.5), # Posiciona na borda direita
        fontsize=10
    )

    # Configurações finais
    ax.set_title('Distribuição de Usuários por Centro', fontsize=16, y= 1.1)
    ax.axis('equal') # Garante que o gráfico seja um círculo
    plt.tight_layout()

    # Salvar o gráfico
    plt.savefig(f"graficos/{arq_saida}")
    print(f"Gráfico Distribuição de Usuários por Centro salvo como '{arq_saida}'.")
    plt.close() # Fecha a figura

# ----------------- EXECUÇÃO PRINCIPAL -----------------

# Carregar os arquivos JSON
try:
    df_ocupacao_mensal = pd.read_json(f"dados/ocupacao_mensal.json")
    df_usuarios_centro = pd.read_json(f"dados/usuarios_centro.json")
except FileNotFoundError:
    print(f"ERRO: Os arquivos não foram encontrados.")
    exit()

# Preparação dos Dados Comuns de Ocupação Mensal
# 1. Filtragem das Partições Relevantes
df_ocupacao_mensal['data_mensal'] = df_ocupacao_mensal['ano'].astype(str) + '-' + df_ocupacao_mensal['mes'].astype(str).str.zfill(2)

# 2. Criação das Métricas
df_ocupacao_mensal['Tempo Médio de Espera (Horas)'] = df_ocupacao_mensal['media_espera_segundos'] / 3600
df_ocupacao_mensal['Tempo Médio de Execução (Horas)'] = df_ocupacao_mensal['media_execucao_segundos'] / 3600
df_ocupacao_mensal['Número de Jobs'] = df_ocupacao_mensal['jobs']

# Ordenar o DataFrame pela data
df_ocupacao_mensal = df_ocupacao_mensal.sort_values(by='data_mensal')

# Lista de cores distintas para o gráfico de pizza
CORES_DISTINTAS = [
    '#1f77b4',  # 1. Azul Metrópole
    '#ff7f0e',  # 2. Laranja Queimado
    '#2ca02c',  # 3. Verde Floresta
    '#d62728',  # 4. Vermelho Escuro
    '#9467bd',  # 5. Roxo Índigo
    '#8c564b',  # 6. Marrom
    '#e377c2',  # 7. Rosa Choque
    '#7f7f7f',  # 8. Cinza Grafite
    '#bcbd22',  # 9. Oliva Claro
    '#17becf',  # 10. Azul Ciano
    '#800080',  # 11. Magenta Escuro
    '#bfff00',  # 12. Verde Lima
    '#ffc300'   # 13. Dourado
]

# Geração dos Gráficos (Chamadas à função)

# Gráfico 1: Tempo Médio de Espera
plot_grafico_linha(
    df_ocupacao_mensal,
    'Tempo Médio de Espera (Horas)',
    'Tempo Médio de Espera (h)',
    'Tempo Médio de Espera por Partição (Mensal)',
    'grafico_tempo_espera.png',
    add_hours_suffix=True
)

# Gráfico 2: Tempo Médio de Execução
plot_grafico_linha(
    df_ocupacao_mensal,
    'Tempo Médio de Execução (Horas)',
    'Tempo Médio de Execução (h)',
    'Tempo Médio de Execução por Partição (Mensal)',
    'grafico_tempo_execucao.png',
    add_hours_suffix=True
)

# Gráfico 3: Número de Jobs
plot_grafico_linha(
    df_ocupacao_mensal,
    'Número de Jobs',
    'Número de Jobs',
    'Número de Jobs por Partição (Mensal)',
    'grafico_numero_jobs.png',
    add_hours_suffix=False
)

# Gráfico 4: Distribuição de Usuários por Centro
plot_grafico_pizza(
    df_usuarios_centro,
    CORES_DISTINTAS,
    'grafico_usuarios_centro.png'
)
