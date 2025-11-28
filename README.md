# Compilador de estatísticas

Scripts para gerar gráficos a serem exibidos no site do npad.

Os dados devem ficar em `dados`.
As imagens de saída devem ser escritas em `graficos`.

## Instalando requisitos

Esse projeto usa ambientes virtuais de python (venv).
No Ubuntu, pode-se instalar o venv com:

```bash
sudo apt install python3-venv
```

Execute os seguintes comandos pra instalar as dependências:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Executando

O script pode ser executado assim:

```bash

./estatistica.py
#ou
./.venv/bin/python estatistica.py
#ou ainda
. .venv/bin/activate
python estatistica.py
```

## Criação dos dados

O arquivo [consulta_usuarios.sql](consulta_usuarios.sql) contém os comandos SQL necessários para a criação do arquivo `usuarios_centro.json`, que é utilizado para a criação do gráfico de distribuição de usuários por centro.

## Dados para teste

Na pasta `dados_teste` contém os arquivos JSON
necessários para a execução do script. Esses arquivos podem ser copiados para a pasta `dados` para que possam ser executados no script.

## Variáveis de Ambiente

Esse projeto utiliza de variáveis de ambiente para obtenção dos dados necessários para a execução do scritp e criação dos gráficos das estatísticas do NPAD. Caso as variavéis não sejam definidas o script por padrão busca os arquivos JSON da pasta `dados`.
Deve ser criado um arquivo `.env` no diretório do projeto com as variáveis de ambiente, que podem ser URLs ou caminhos de arquivos locais. Elas tem a seguinte definição:

```
FONTE_<nome_do_arquivo> = "adicionar_aqui_a_url_ou_caminho_do_arquivo_local"

Exemplo:
FONTE_OCUPACAO_MENSAL = "https://<URL_fonte>/ocupacao_mensal.json"
FONTE_USUARIOS_CENTRO = "<PATH_local>/usuarios_centro.json"
```

Pode ser utilizado o arquivo `env.dev` deixado nesse repositório como exemplo dos nomes das variáveis de ambiente utilizadas no script.
