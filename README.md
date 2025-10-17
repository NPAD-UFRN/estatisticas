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
