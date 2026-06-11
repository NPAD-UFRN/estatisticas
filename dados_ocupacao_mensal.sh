#!/bin/bash

#Script que coleta os dados necessários para o script ocupacao_mensal.py.
#Ele deve calcular as datas de início e fim, e executar o seguinte comando:
#sacct -X -P -S "$START_DATE" -E "$END_DATE" \
#          --format=JobID,Partition,Submit,Start,end --noheader
#Seja o mês de hoje Mh e seja o ano de hoje Ah, as datas são:
#START_DATE = "Mh/01/Ah-1 00:00:00"
#END_DATE = "Mh/01/Ah 00:00:00"

#Obter o mês e ano atuais
MONTH=$(date +%m)
YEAR=$(date +%Y)
#Calcular as datas de início e fim
START_DATE="${MONTH}/01/$((YEAR-1)) 00:00:00"
END_DATE="${MONTH}/01/${YEAR} 00:00:00"
#Executar o comando sacct e salvar a saída em um arquivo
sacct -X -P -S "$START_DATE" -E "$END_DATE" \
    --format=JobID,Partition,Submit,Start,end --noheader
