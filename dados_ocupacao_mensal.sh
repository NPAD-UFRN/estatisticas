#!/bin/bash

#Script que coleta os dados necessários para o script ocupacao_mensal.py.
#Seja o mês de hoje Mh e seja o ano de hoje Ah, as datas são:
#START_DATE = "(Ah-1)-Mh-01 00:00:00"
#END_DATE = "Ah-Mh-01 00:00:00"

#Obter o mês e ano atuais
MONTH=$(date +%m)
YEAR=$(date +%Y)
#Calcular as datas de início e fim
START_DATE="$((YEAR-1))-${MONTH}-01 00:00:00"
END_DATE="${YEAR}-${MONTH}-01 00:00:00"
#Executar o comando sacct e salvar a saída em um arquivo
sacct -a -X -P -S "$START_DATE" -E "$END_DATE" \
    --format=JobID,Partition,Submit,Start,end --noheader
