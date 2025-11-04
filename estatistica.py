#!/usr/bin/env -S .venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def criar_grafico_linha(df_plot, metric_col, y_label, titulo, arq_saida, add_hours_suffix=False):
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
    
def criar_grafico_pizza(df_plot, cores, arq_saida):
    """Gera e salva um gráfico de pizza para a distribuição de usuários por centro."""
    
    # Contar usuários por centro
    contagem = df_plot['centro'].value_counts()

    # Separar centros principais (>5 usuários) e outros (<=5 usuários)
    centros_principais = contagem[contagem > 5]
    centros_outros = contagem[contagem <= 5]

    # Criar série final com "Outros" se houver centros pequenos
    if len(centros_outros) > 0:
        outros_total = centros_outros.sum()
        contagem_final = pd.concat([
            centros_principais,
            pd.Series({'Outros': outros_total})
        ])
    else:
        contagem_final = centros_principais

    # Extrair siglas dos centros usando a nova função
    labels = []
    sizes = []

    for centro, count in contagem_final.items():
        if centro == 'Outros':
            labels.append('Outros')
        else:
            labels.append(simplificar_nome(centro)) # Usar a função aqui
        sizes.append(count)

    # Criar labels para a legenda com formato: "SIGLA (N)"
    legend_labels = []
    for label, size in zip(labels, sizes):
        if label == 'Outros':
            # Extrair siglas e contagens dos centros agrupados em "Outros" usando a nova função
            centros_info = []
            for centro, count in centros_outros.items():
                centros_info.append(f'{simplificar_nome(centro)} ({count})')
            centros_str = ',\n'.join(centros_info)
            legend_labels.append(f'{label} ({size}):\n{centros_str}')
        else:
            legend_labels.append(f'{label} ({size})')

    # Configurar figura
    fig, ax = plt.subplots(figsize=(15, 10))

    # Criar gráfico de pizza sem autopct (vamos adicionar manualmente)
    wedges, texts = ax.pie(
        sizes,
        wedgeprops={'edgecolor': 'black', 'linewidth': 1},
        colors=cores
    )

    # Adicionar valores absolutos e percentuais manualmente
    for i, (wedge, size) in enumerate(zip(wedges, sizes)):
        # Calcular ângulo e posição
        ang = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
        x = 1.1 * wedge.r * np.cos(np.radians(ang))
        y = 1.1 * wedge.r * np.sin(np.radians(ang))

        # Calcular percentual
        percentual = 100 * size / sum(sizes)

        # Adicionar texto com valor absoluto e percentual
        ax.text(x, y, f'{size}\n({percentual:.1f}%)',
                ha='center', va='center',
                fontsize=13,
                color='black')

    # Adicionar título
    plt.title('Distribuição de usuários por centro',
              fontsize=20)

    # Adicionar legenda
    plt.legend(
        legend_labels,
        title='Centros (Usuários)',
        loc='center left',
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=12,
        title_fontsize=14
    )

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
criar_grafico_linha(
    df_ocupacao_mensal,
    'Tempo Médio de Espera (Horas)',
    'Tempo Médio de Espera (h)',
    'Tempo Médio de Espera por Partição (Mensal)',
    'grafico_tempo_espera.png',
    add_hours_suffix=True
)

# Gráfico 2: Tempo Médio de Execução
criar_grafico_linha(
    df_ocupacao_mensal,
    'Tempo Médio de Execução (Horas)',
    'Tempo Médio de Execução (h)',
    'Tempo Médio de Execução por Partição (Mensal)',
    'grafico_tempo_execucao.png',
    add_hours_suffix=True
)

# Gráfico 3: Número de Jobs
criar_grafico_linha(
    df_ocupacao_mensal,
    'Número de Jobs',
    'Número de Jobs',
    'Número de Jobs por Partição (Mensal)',
    'grafico_numero_jobs.png',
    add_hours_suffix=False
)

# Gráfico 4: Distribuição de Usuários por Centro
criar_grafico_pizza(
    df_usuarios_centro,
    CORES_DISTINTAS,
    'grafico_usuarios_centro.png'
)
