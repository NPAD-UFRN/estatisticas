#!/usr/bin/env -S .venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def plot_data(df_plot, metric_col, y_label, titulo, arq_saida, add_hours_suffix=False):
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

# ----------------- EXECUÇÃO PRINCIPAL -----------------

# 1. Carregar o arquivo JSON
try:
    df = pd.read_json(f"dados/ocupacao_mensal.json")
except FileNotFoundError:
    print(f"ERRO: O arquivo 'ocupacao_mensal.json' não foi encontrado.")
    exit()

# 2. Preparação dos Dados Comuns
df['data_mensal'] = df['ano'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)

# 3. Criação das Métricas
df['Tempo Médio de Espera (Horas)'] = df['media_espera_segundos'] / 3600
df['Tempo Médio de Execução (Horas)'] = df['media_execucao_segundos'] / 3600
df['Número de Jobs'] = df['jobs']

# Ordenar o DataFrame pela data
df = df.sort_values(by='data_mensal')

# 4. Geração dos Gráficos (Chamadas à função)

# Gráfico 1: Tempo Médio de Espera
plot_data(
    df,
    'Tempo Médio de Espera (Horas)',
    'Tempo Médio de Espera (h)',
    'Tempo Médio de Espera por Partição (Mensal)',
    'grafico_tempo_espera.png',
    add_hours_suffix=True
)

# Gráfico 2: Tempo Médio de Execução
plot_data(
    df,
    'Tempo Médio de Execução (Horas)',
    'Tempo Médio de Execução (h)',
    'Tempo Médio de Execução por Partição (Mensal)',
    'grafico_tempo_execucao.png',
    add_hours_suffix=True
)

# Gráfico 3: Número de Jobs
plot_data(
    df,
    'Número de Jobs',
    'Número de Jobs',
    'Número de Jobs por Partição (Mensal)',
    'grafico_numero_jobs.png',
    add_hours_suffix=False
)
