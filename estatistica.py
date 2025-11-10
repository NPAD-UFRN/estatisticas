#!/usr/bin/env -S .venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

def criar_grafico_linha(df, metric_col, y_label, titulo, arq_saida, add_sufixo_h=False):
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
    
    # Configuração de cores
    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']
    color_cycle = plt.cycler(color=colors)
    plt.gca().set_prop_cycle(color_cycle)

    for particao in particoes:
        # Filtra e garante a ordenação por data
        subset = df[df['particao'] == particao].sort_values(by='data_mensal')
        
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
    plt.savefig(f"graficos/{arq_saida}")
    print(f"Gráfico '{titulo}' salvo como '{arq_saida}'.")
    plt.close()

# Simplificar os nomes dos centros
def simplificar_nome(nome):
    if ' - ' in nome:
        return nome.split(' - ')[-1].replace('.', '')
    
def criar_grafico_pizza(df, categorias, valores_col=None, titulo='Gráfico de Pizza', 
                        arq_saida='grafico_pizza.png', cores=None, 
                        agrupar_pequenos=False, threshold=5, adicionar_percentual=True,
                        processar_labels=None, subplots=None, legenda_unica=False):
    """ Gera e salva gráfico(s) de pizza para as métricas esécificadas."""
    
    # Cores padrão
    if cores is None:
        cores = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#800080', '#bfff00', '#ffc300', '#ff9999', '#66b3ff', '#99ff99'
        ]
    
    # Gráfico único de distribuição
    if subplots is None:
        if valores_col:
            contagem = df.groupby(categorias)[valores_col].sum()
        else:
            contagem = df[categorias].value_counts()
        
        # Agrupar pequenos valores em "Outros"
        if agrupar_pequenos:
            principais = contagem[contagem > threshold]
            outros = contagem[contagem <= threshold]
            
            if len(outros) > 0:
                contagem_final = pd.concat([
                    principais,
                    pd.Series({'Outros': outros.sum()})
                ])
            else:
                contagem_final = principais
        else:
            contagem_final = contagem
        
        # Processar labels
        labels = []
        sizes = []
        
        for cat, count in contagem_final.items():
            if cat == 'Outros':
                labels.append('Outros')
            else:
                labels.append(processar_labels(cat) if processar_labels else cat)
            sizes.append(count)
        
        # Criar labels para legenda
        legend_labels = []
        for label, size in zip(labels, sizes):
            if label == 'Outros' and agrupar_pequenos:
                centros_info = []
                for cat, count in outros.items():
                    cat_label = processar_labels(cat) if processar_labels else cat
                    centros_info.append(f'{cat_label} ({count})')
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
            colors=cores[:len(sizes)]
        )
        
        # Adicionar valores e percentuais
        if adicionar_percentual:
            for wedge, size in zip(wedges, sizes):
                ang = (wedge.theta2 - wedge.theta1) / 2 + wedge.theta1
                x = 1.1 * wedge.r * np.cos(np.radians(ang))
                y = 1.1 * wedge.r * np.sin(np.radians(ang))
                percentual = 100 * size / sum(sizes)
                ax.text(x, y, f'{size}\n({percentual:.1f}%)',
                       ha='center', va='center', fontsize=13, color='black')
        
        plt.title(titulo, fontsize=20)
        plt.legend(legend_labels, title='Centros (Usuários)',
                  loc='center left', bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=12, title_fontsize=14)
    
    # Múltiplos gráficos de pizza (subplots)
    else:
        linhas, colunas = subplots
        fig, axes = plt.subplots(linhas, colunas, figsize=(15, 16))
        fig.suptitle(titulo, fontsize=16, fontweight='bold', y=0.995)
        
        if isinstance(categorias, list):
            cols_valores = categorias
        else:
            cols_valores = [categorias]
        
        for idx, row in df.iterrows():
            if idx >= linhas * colunas:
                break
                
            linha = idx // colunas
            coluna = idx % colunas
            ax = axes[linha, coluna] if linhas > 1 else axes[coluna]
            
            # Extrair valores para este gráfico
            valores = [row[col] for col in cols_valores]
            
            # Criar gráfico de pizza
            wedges, texts, autotexts = ax.pie(
                valores,
                colors=cores[:len(valores)],
                autopct='%1.1f%%' if adicionar_percentual else None,
                wedgeprops={'edgecolor': 'black', 'linewidth': 1},
                startangle=90
            )
            
            # Configurar título
            titulo_subplot = row.get('mes', f'Item {idx+1}')
            ax.set_title(titulo_subplot, fontsize=12, fontweight='bold')
            
            # Melhorar aparência dos percentuais
            if adicionar_percentual and autotexts:
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(10)
                    autotext.set_fontweight('bold')
        
        # Criar legenda única
        if legenda_unica:
            # Usar os nomes das colunas como labels da legenda
            labels_legenda = [col.capitalize() for col in cols_valores]
            fig.legend(labels_legenda, loc='lower center', ncol=len(cols_valores),
                      fontsize=12, frameon=True, bbox_to_anchor=(0.5, -0.02))
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.99])
    plt.savefig(f"graficos/{arq_saida}", dpi=300, bbox_inches='tight')
    print(f"Gráfico '{titulo}' salvo como '{arq_saida}'.")
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
    metric_col='Tempo Médio de Espera (Horas)',
    y_label='Tempo Médio de Espera (h)',
    titulo='Tempo Médio de Espera por Partição (Mensal)',
    arq_saida='grafico_tempo_espera.png',
    add_sufixo_h=True
)

# Gráfico 2: Tempo Médio de Execução
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metric_col='Tempo Médio de Execução (Horas)',
    y_label='Tempo Médio de Execução (h)',
    titulo='Tempo Médio de Execução por Partição (Mensal)',
    arq_saida='grafico_tempo_execucao.png',
    add_sufixo_h=True
)

# Gráfico 3: Número de Jobs
criar_grafico_linha(
    df=df_ocupacao_mensal,
    metric_col='Número de Jobs',
    y_label='Número de Jobs',
    titulo='Número de Jobs por Partição (Mensal)',
    arq_saida='grafico_numero_jobs.png',
    add_sufixo_h=False
)

# Gráfico 4: Distribuição de Usuários por Centro
criar_grafico_pizza(
    df=df_usuarios_centro,
    categorias='centro',
    titulo='Distribuição de usuários por centro',
    arq_saida='grafico_usuarios_centro.png',
    cores=CORES_DISTINTAS,
    agrupar_pequenos=True,
    threshold=5,
    processar_labels=simplificar_nome,
    adicionar_percentual=True
)

# Gráfico 5: Atividade do supercomputador, últimos 12 meses
criar_grafico_pizza(
    df=df_atividade,
    categorias=['ocioso', 'utilizado', 'inativo'],
    titulo='Atividade do supercomputador, últimos 12 meses',
    arq_saida='atividade_supercomputador.png',
    cores=CORES_DISTINTAS,
    subplots=(4, 3),  # 4 linhas x 3 colunas
    legenda_unica=True,
    adicionar_percentual=True
)