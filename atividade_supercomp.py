#!/usr/bin/env python3

import subprocess
import json
import datetime
import sys

"""
Script que coleta dados de utilização de CPU dos últimos 12 meses usando o
comando sreport.

O comando do srport utilizado é:
sreport cluster utilization start=MM/DD/YY end=MM/DD/YY -t percent -T cpu -nP

Uma saida de exemplo do comando é:
    ufrn|cpu|29.08%|6.20%|15.62%|34.28%|14.83%|100.00%
    onde:
    - os dois primeiros campos são sempre ufrn e cpu
    - os demais campos são, respectivamente:
        - allocated
        - down
        - plnd_down
        - idle
        - planned
        - reported (sempre 100%)

O primeiro argumento do script é um arquivo de entrada, com a saída gerada pelo
sreport.
O script processa esses dados e gera um json. Um exemplo de saída:
Os dados de entrada não tem data, mas deve-se supor que as linhas representam os
últimos 12 meses em ordem cronolíogica.

[
  { "mes": "11-2024", "ocioso": 34, "utilizado": 50, "inativo": 16 },
  { "mes": "12-2024", "ocioso": 45, "utilizado": 38, "inativo": 17 },
  { "mes": "01-2025", "ocioso": 28, "utilizado": 61, "inativo": 11 },
  { "mes": "02-2025", "ocioso": 53, "utilizado": 28, "inativo": 19 },
  { "mes": "03-2025", "ocioso": 25, "utilizado": 64, "inativo": 11 },
  { "mes": "04-2025", "ocioso": 19, "utilizado": 73, "inativo": 8 },
  { "mes": "05-2025", "ocioso": 50, "utilizado": 33, "inativo": 17 },
  { "mes": "06-2025", "ocioso": 41, "utilizado": 40, "inativo": 19 },
  { "mes": "07-2025", "ocioso": 31, "utilizado": 55, "inativo": 14 },
  { "mes": "08-2025", "ocioso": 62, "utilizado": 21, "inativo": 17 },
  { "mes": "09-2025", "ocioso": 24, "utilizado": 67, "inativo": 9 },
  { "mes": "10-2025", "ocioso": 38, "utilizado": 45, "inativo": 17 }
]

Onde: ocioso = idle
       utilizado = allocated + planned
       inativo = down + plnd_down
"""

#Classe que armazena registros da entrada do sreport
class SReportRecord:
    def __init__(self, line, mes):
        parts = line.split('|')
        self.tres_name = parts[1].strip()
        self.allocated = float(parts[2].replace('%', ''))
        self.down      = float(parts[3].replace('%', ''))
        self.plnd_dow  = float(parts[4].replace('%', ''))
        self.idle      = float(parts[5].replace('%', ''))
        self.planned   = float(parts[6].replace('%', ''))
        self.mes = mes

#Classe que armazena os registros de saida:
class MonthlyReport:
    def __init__(self, month_year):
        self.month_year = month_year
        self.utilizado = 0
        self.ocioso = 0
        self.inativo = 0

def round_to_100(values):
    int_parts = [int(v) for v in values]
    remainders = [(values[i] - int_parts[i], i) for i in range(len(values))]
    remainders.sort(key=lambda x: x[0], reverse=True)

    diff = 100 - sum(int_parts)

    for i in range(diff):
        category_index = remainders[i][1]
        int_parts[category_index] += 1

    return int_parts

def parse_report(lines, hoje):
    """Lê a saida do comando sreport e gera uma lista de objetos SreportRecord
Os meses são inferidos a partir da ordem das linhas, assumindo que a primeira
linha corresponde ao mês mais antigo e a última linha ao mês de hoje.
Hoje é um datetime com a data que se supoe ser hoje."""
    records = []
    for i, line in enumerate(lines):
        if not line.strip():            continue
        mes = (hoje - datetime.timedelta(days=30*(11 - i))).strftime('%m-%Y')
        record = SReportRecord(line, mes)
        records.append(record)
    return records  

def process_records(records):
    """Processa os registros de entrada e gera uma lista de objetos
    MonthlyReport, um para cada mês"""
    monthly_reports = {}
    for record in records:
        if record.tres_name != "cpu":
            continue

        if record.mes not in monthly_reports:
            monthly_reports[record.mes] = MonthlyReport(record.mes)

        monthly_report = monthly_reports[record.mes]
        monthly_report.utilizado += record.allocated + record.planned
        monthly_report.ocioso += record.idle
        monthly_report.inativo += record.down + record.plnd_dow

    return list(monthly_reports.values())

def output_json(monthly_reports):
    """Gera a saida json a partir dos objetos MonthlyReport"""
    output = []
    for report in monthly_reports:
        total = report.utilizado + report.ocioso + report.inativo
        if total == 0:
            continue

        utilizado = round(report.utilizado * 100 / total)
        ocioso = round(report.ocioso * 100 / total)
        inativo = round(report.inativo * 100 / total)

        # Ajuste para garantir que a soma seja 100%
        utilizado, ocioso, inativo = round_to_100([utilizado, ocioso, inativo])

        output.append({
            "mes": report.month_year,
            "utilizado": utilizado,
            "ocioso": ocioso,
            "inativo": inativo
        })
    return output

def main():
   hoje = datetime.datetime.now()
   if sys.argv[1:]:
       with open(sys.argv[1], 'r') as f:
           lines = f.readlines()
       records = parse_report(lines, hoje)
       monthly_reports = process_records(records)
       output = output_json(monthly_reports)
       print(json.dumps(output, indent=2))
   else:
        print("No input file provided")

if __name__ == "__main__":
    main()
