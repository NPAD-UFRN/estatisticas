Considere que o comando

```bash
sreport cluster utilization start=2026-03-01 end=2026-06-01 -t percent -T cpu -nP
```

gera uma saída como
```
ufrn|cpu|29.08%|6.20%|15.62%|34.28%|14.83%|100.00%
```

Sua missão é escrever um script bash chamado `atividade_supercomp.sh` que
executa o sreport como mostrado acima, e gera 12 linhas, correspondentes aos
últimos 12 meses, em ordem cronológica.

```bash
#!/bin/bash
# Script para gerar relatório de utilização do cluster nos últimos 12 meses
# Loop para os últimos 12 meses
for i in {0..11}; do
    # Calcula a data de início e fim para o mês atual
    start_date=$(date -d "$i month ago" +"%Y-%m-01")
    end_date=$(date -d "$i month ago +1 month -1 day" +"%Y-%m-%d")
    # Executa o comando sreport e formata a saída
    sreport cluster utilization start=$start_date end=$end_date -t percent -T
    cpu -nP
done
``` 


