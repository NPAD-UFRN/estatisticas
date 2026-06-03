Sua missão é criar um script python chamado `ocupacao_mensal.py` que gere o arquivo `ocupacao_mensal.json`, o qual mostra números sobre os jobs do slurm que rodam em um cluster.

O arquivo `ocupacao_mensal.json` tem esse formato:

```
[
...
 {"ano": 2023, "mes": 12, "particao": "gpu-4-a100", "jobs": 1, "media_espera_segundos": 205733, "media_espera_formatado": "2d 9h 8m 53s", "media_execucao_segundos": 55449, "media_execucao_formatado": "15h 24m 9s"},
{"ano": 2023, "mes": 12, "particao": "intel-128", "jobs": 6, "media_espera_segundos": 0, "media_espera_formatado": "0s", "media_execucao_segundos": 316972, "media_execucao_formatado": "3d 16h 2m 52s"},
...
{"ano": 2024, "mes": 1, "particao": "gpu-4-a100", "jobs": 44, "media_espera_segundos": 325813, "media_espera_formatado": "3d 18h 30m 13s", "media_execucao_segundos": 47428, "media_execucao_formatado": "13h 10m 28s"},
{"ano": 2024, "mes": 1, "particao": "intel-128", "jobs": 5564, "media_espera_segundos": 4153, "media_espera_formatado": "1h 9m 13s", "media_execucao_segundos": 3672, "media_execucao_formatado": "1h 1m 12s"},
...
]
```

Ou seja, é uma lista de objetos json. Cada objeto json tem dados de um mês M respectivo. O arquivo deve seguir ordem cronológica. Os campos são:
- ano: o ano como inteiro
- mes: o mes como inteiro, de 1 a 12
- particao: refere-se à partição slurm do cluster 
- jobs: quantos jobs no total estiveram rodando no mês M, independente de terem iniciado ou terminado em meses diferentes.
- `media_espera_`...: para cada job que começou a rodar nesse mês, quanto tempo levou desde a submissão até o início da execução. uma média desses valores, em dois formatos (em segundos, e como string formatada)
- `media_execucao_`: semelhante ao campo anterior, mas diz quanto tempo duraram os jobs que encerraram no mês M.

Um exemplo do arquivo está em dados_teste. É um arquivo muito grande que você não deve ler inteiro, para não preencher seu contexto.

As partições que devem ser consideradas são: amd-512, amd-3tb, gpu-4-a100, gpu-8-v100, gpu-8-h100, gpu-4-h200, intel-128, intel-256, intel-512.

O script `ocupacao_mensal.py` não irá rodar nesta máquina, mas sim em um cluster ao qual essa máquina não tem acesso. Você não será capaz de testar o script aqui. A validação deve se resumir a verificar se a sintaxe está correta.

A fonte de dados deve vir do seguinte comando, o qual deve ser executado uma única vez no script `ocupacao_mensal.py`:

```bash

sacct -X -P -S "$START_DATE" -E "$END_DATE" --format=JobID,Partition,Submit,Start,Elapsed,State --noheader
```

O script deve calcular START_DATE e END_DATE para que o json gerado mostre os 12 últimos meses, até o final do mês anterior ao do dia de hoje.
Não é preciso considerar nenhum job além dos que forem exibidos por esse comando.

Você pode usar outros comandos do linux ou outros pacotes de python conforme julgar necessário.
Uma cópia da manpage do sacct está em sacct.txt. Também é um arquivo grande, então leia somente o que precisar.

