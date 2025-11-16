#!/usr/bin/env -S .venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def criar_grafico_linha(df, metrica_col, y_label, titulo, arquivo_saida, add_sufixo_h=False):
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

    particoes = df['particao'].unique()
    for particao in particoes:
        # Filtra e garante a ordenação por data
        subset = df[df['particao'] == particao].sort_values(by='data_mensal')
        
        if not subset.empty:
            plt.plot(
                subset['data_mensal'],
                subset[metrica_col],
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
    x_labels = df['data_mensal'].unique()
    if len(x_labels) > 15:
        step = int(np.ceil(len(x_labels) / 15))
        plt.xticks(x_labels[::step], rotation=45, ha='right')
    else:
        plt.xticks(x_labels, rotation=45, ha='right')
        
    # Posiciona a legenda fora do gráfico
    plt.legend(loc='lower center', bbox_to_anchor=(0.5, 1.05), 
            ncol=len(particoes) // 2 + 1, fontsize=10)
    
    plt.tight_layout()
    plt.savefig(f"graficos/{arquivo_saida}", dpi=300, bbox_inches='tight')
    print(f"Gráfico '{titulo}' salvo como '{arquivo_saida}'.")
    plt.close()

# Simplificar os nomes dos centros
def simplificar_nome(nome):
    if ' - ' in nome:
        return nome.split(' - ')[-1].replace('.', '')
    
def criar_grafico_pizza(df, cores, arquivo_saida):
    """Gera e salva um gráfico de pizza para a distribuição de usuários por centro."""
    
    # Separar centros principais (>5 usuários) e outros (<=5 usuários)
    df_principais = df[df['usuarios'] > 5]
    df_outros = df[df['usuarios'] <= 5]
    
    # Criar dicionário final com "Outros" se houver centros pequenos
    if len(df_outros) > 0:
        outros_total = df_outros['usuarios'].sum()
        # Criar série com centros principais
        contagem_final = pd.Series(df_principais['usuarios'].values, 
                                   index=df_principais['centro'].values)
        # Adicionar "Outros"
        contagem_final['Outros'] = outros_total
    else:
        contagem_final = pd.Series(df_principais['usuarios'].values, 
                                   index=df_principais['centro'].values)
    
    labels = []
    sizes = []
    for centro, count in contagem_final.items():
        labels.append(centro)
        sizes.append(count)
    
    # Criar labels para a legenda com formato: "SIGLA (N)"
    legend_labels = []
    for label, size in zip(labels, sizes):
        if label == 'Outros':
            centros_info = []
            for _, row in df_outros.iterrows():
                centro = row['centro']
                count = row['usuarios']
                centros_info.append(f'{centro} ({count})')
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
    plt.savefig(f"graficos/{arquivo_saida}", dpi=300, bbox_inches='tight')
    print(f"Gráfico 'Distribuição de Usuários por Centro' salvo como '{arquivo_saida}'.")
    plt.close()


def criar_grafico_barras(df, titulo, subtitulo, arquivo_saida, xlabel='Mês', ylabel='Porcentagem (%)'):
    """ Cria um gráfico de barras empilhadas para a atividade do supercomputador. """
    
    # Cria a figura
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Prepara os dados para o gráfico
    categorias = ['ocioso', 'utilizado', 'inativo']
    meses = df['mes'].tolist()
    
    # Cria as barras empilhadas
    bottom = [0] * len(df)
    
    for i, categoria in enumerate(categorias):
        valores = df[categoria].tolist()
        ax.bar(meses, valores, bottom=bottom, label=categoria.capitalize(), edgecolor='white', linewidth=0.5)
        # Atualiza o bottom para a próxima camada
        bottom = [bottom[j] + valores[j] for j in range(len(valores))]
    
    # Configurações do gráfico
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    plt.suptitle(titulo, fontsize=16, y=0.96)
    plt.title(subtitulo, fontsize=12, y=1.1)
    
    
    # Legenda centralizada abaixo do título
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.08), 
              ncol=3, framealpha=0.9, frameon=True)
    
    # Rotaciona os rótulos do eixo X
    plt.xticks(rotation=45, ha='right')
    
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Ajusta o layout para evitar cortes
    plt.tight_layout()
    
    # Salva o gráfico
    plt.savefig(f"graficos/{arquivo_saida}", dpi=300, bbox_inches='tight')
    print(f"Gráfico '{titulo}' salvo como '{arquivo_saida}'")
    
    # Fecha a figura para liberar memória
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
    metrica_col='Tempo Médio de Espera (Horas)',
    y_label='Tempo Médio de Espera (h)',
    titulo='Tempo Médio de Espera por Partição (Mensal)',
    arquivo_saida='tempo_espera.png',
    add_sufixo_h=True
)

# Gráfico 2: Tempo Médio de Execução
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metrica_col='Tempo Médio de Execução (Horas)',
    y_label='Tempo Médio de Execução (h)',
    titulo='Tempo Médio de Execução por Partição (Mensal)',
    arquivo_saida='tempo_execucao.png',
    add_sufixo_h=True
)

# Gráfico 3: Número de Jobs
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metrica_col='Número de Jobs',
    y_label='Número de Jobs',
    titulo='Número de Jobs por Partição (Mensal)',
    arquivo_saida='numero_jobs.png',
    add_sufixo_h=False
)

# Gráfico 4: Distribuição de Usuários por Centro
criar_grafico_pizza(
    df=df_usuarios_centro,
    arquivo_saida='usuarios_centro.png',
    cores=CORES_DISTINTAS
)

# Gráfico 5: Atividade do supercomputador, últimos 12 meses
criar_grafico_barras(
    df=df_atividade,
    titulo="Atividade do supercomputador, últimos 12 meses",
    subtitulo="Percentual de utilização de todas as CPUs de todos os nós do supercomputador",
    arquivo_saida="atividade_supercomp.png",
    xlabel='Mês',
    ylabel='Porcentagem (%)'
)