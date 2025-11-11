#!/usr/bin/env -S .venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def criar_grafico_linha(df, metric_cols, y_label, titulo, arq_saida, add_sufixo_h=False, col_data='data_mensal'):
    """Gera e salva um gráfico de linha para a métrica especificada."""
    
    # Cria uma nova figura para cada gráfico
    plt.figure(figsize=(15, 8))
    ax = plt.gca()

    # --- Formatação do Eixo Y (Adicionar 'h' nas horas) ---
    if add_sufixo_h:
        def hours_formatter(x, pos):
            # Formata o valor com uma casa decimal e adiciona o ' h'
            return f'{x:.1f} h'
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(hours_formatter))
    
    # Configuração de cores
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    color_cycle = plt.cycler(color=colors)
    plt.gca().set_prop_cycle(color_cycle)

    if isinstance(metric_cols, str):
        particoes = df['particao'].unique()
        for particao in particoes:
            # Filtra e garante a ordenação por data
            subset = df[df['particao'] == particao].sort_values(by='data_mensal')
            
            if not subset.empty:
                plt.plot(
                    subset['data_mensal'],
                    subset[metric_cols],
                    marker='o',
                    linestyle='-',
                    linewidth=2,
                    markersize=5,
                    label=particao
                )
    else:
        # Garantir que metric_cols é uma lista
        if isinstance(metric_cols, str):
            metric_cols = [metric_cols]
        
        # Ordenar DataFrame por data
        df_sorted = df.sort_values(by=col_data)
        
        # Plotar cada coluna
        for metric_col in metric_cols:
            plt.plot(
                df_sorted[col_data],
                df_sorted[metric_col],
                marker='o',
                linestyle='-',
                linewidth=2,
                markersize=5,
                label=metric_col.capitalize()
            )

    # Configurações do gráfico
    plt.title(titulo, fontsize=16, y=1.2)
    plt.xlabel('Ano-Mês', fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Configurar ticks do eixo X
    x_labels = df['data_mensal'].unique()
    if len(x_labels) > 15:
        step = int(np.ceil(len(x_labels) / 15))
        plt.xticks(x_labels[::step], rotation=45, ha='right')
    else:
        plt.xticks(x_labels, rotation=45, ha='right')
        
    # Posiciona a legenda fora do gráfico
    if isinstance(metric_cols, str):
        plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), 
               ncol=len(particoes) // 2 + 1, fontsize=10)
    else:
        plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), 
               ncol=len(metric_cols), fontsize=10)

    plt.tight_layout()
    plt.savefig(f"graficos/{arq_saida}", dpi=300, bbox_inches='tight')
    print(f"Gráfico '{titulo}' salvo como '{arq_saida}'.")
    plt.close()

# Simplificar os nomes dos centros
def simplificar_nome(nome):
    if ' - ' in nome:
        return nome.split(' - ')[-1].replace('.', '')
    
def criar_grafico_pizza(df, cores, arq_saida):
    """Gera e salva um gráfico de pizza para a distribuição de usuários por centro."""
    
    # Contar usuários por centro
    contagem = df['centro'].value_counts()

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

    labels = []
    sizes = []

    for centro, count in contagem_final.items():
        if centro == 'Outros':
            labels.append('Outros')
        else:
            labels.append(simplificar_nome(centro))
        sizes.append(count)

    # Criar labels para a legenda com formato: "SIGLA (N)"
    legend_labels = []
    for label, size in zip(labels, sizes):
        if label == 'Outros':
            centros_info = []
            for centro, count in centros_outros.items():
                centros_info.append(f'{simplificar_nome(centro)} ({count})')
            centros_str = ',\n'.join(centros_info)
            legend_labels.append(f'{label} ({size}):\n{centros_str}')
        else:
            legend_labels.append(f'{label} ({size})')

    # Configurar figura
    fig, ax = plt.subplots(figsize=(15, 10))

    # Criar gráfico de pizza
    wedges, texts = ax.pie(
        sizes,
        wedgeprops={'edgecolor': 'black', 'linewidth': 1},
        colors=cores
    )

    # Adicionar valores absolutos e percentuais
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
    plt.savefig(f"graficos/{arq_saida}", dpi=300, bbox_inches='tight')
    print(f"Gráfico 'Distribuição de Usuários por Centro' salvo como '{arq_saida}'.")
    plt.close()

# ----------------- EXECUÇÃO PRINCIPAL -----------------

# Carregar os arquivos JSON
try:
    df_ocupacao_mensal = pd.read_json("dados/ocupacao_mensal.json")
    df_usuarios_centro = pd.read_json("dados/usuarios_centro.json")
    df_atividade = pd.read_json("dados/atividade_supercomp.json")
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

# Preparação dos Dados de Atividade do Supercomputador
# Converter coluna 'mes' de MM-YYYY para formato datetime e criar data_mensal ordenável
df_atividade['data_mensal'] = pd.to_datetime(df_atividade['mes'], format='%m-%Y').dt.strftime('%Y-%m')
# Manter 'mes' original para exibição
df_atividade['mes_display'] = df_atividade['mes']

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
    '#ff9999',  # 14. Rosa Claro
    '#66b3ff',  # 15. Azul Claro
    '#99ff99'   # 16. Verde Claro
]

# Geração dos Gráficos (Chamadas à função)

# Gráfico 1: Tempo Médio de Espera
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metric_cols='Tempo Médio de Espera (Horas)',
    y_label='Tempo Médio de Espera (h)',
    titulo='Tempo Médio de Espera por Partição (Mensal)',
    arq_saida='grafico_tempo_espera.png',
    add_sufixo_h=True
)

# Gráfico 2: Tempo Médio de Execução
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metric_cols='Tempo Médio de Execução (Horas)',
    y_label='Tempo Médio de Execução (h)',
    titulo='Tempo Médio de Execução por Partição (Mensal)',
    arq_saida='grafico_tempo_execucao.png',
    add_sufixo_h=True
)

# Gráfico 3: Número de Jobs
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metric_cols='Número de Jobs',
    y_label='Número de Jobs',
    titulo='Número de Jobs por Partição (Mensal)',
    arq_saida='grafico_numero_jobs.png',
    add_sufixo_h=False
)

# Gráfico 4: Distribuição de Usuários por Centro
criar_grafico_pizza(
    df=df_usuarios_centro,
    arq_saida='grafico_usuarios_centro.png',
    cores=CORES_DISTINTAS
)

# Gráfico 5: Atividade do supercomputador, últimos 12 meses
criar_grafico_linha(
    df=df_atividade,
    metric_cols=['ocioso', 'utilizado', 'inativo'],  # Lista de colunas
    y_label='Porcentagem (%)',
    titulo='Atividade do supercomputador, últimos 12 meses',
    arq_saida='grafico_atividade_supercomp.png',
    add_sufixo_h=False,
    col_data='data_mensal'
)