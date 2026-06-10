#!/bin/bash
# Script para gerar relatório de utilização do cluster nos últimos 12 meses
# Loop para os últimos 12 meses
for i in {0..11}; do
    # Calcula a data de início e fim para o mês atual
    start_date=$(date -d "$i month ago" +"%Y-%m-01")
    end_date=$(date -d "$i month ago +1 month -1 day" +"%Y-%m-%d")
    # Executa o comando sreport e formata a saída
    sreport cluster utilization start=$start_date end=$end_date -t percent -T cpu -nP
done

