#!/usr/bin/env python3
"""
Script para gerar ocupacao_mensal.json com estatísticas de jobs do Slurm.

Gera dados para os últimos 12 meses (começando do mês anterior),
ordenados em ordem crescente.

Partições consideradas:
  amd-512, amd-3tb, gpu-4-a100, gpu-8-v100, gpu-8-h100, gpu-4-h200,
  intel-128, intel-256, intel-512

Comando Slurm usado:
  sacct -X -P -S "$START_DATE" -E "$END_DATE" \
          --format=JobID,Partition,Submit,Start,end --noheader

Este script deve funcionar com python 3.6 ou superior.
"""

import json
import subprocess
import sys
from collections import defaultdict
from datetime import datetime


PARTICOES = [
    "amd-512", "amd-3tb", "gpu-4-a100", "gpu-8-v100", "gpu-8-h100",
    "gpu-4-h200", "intel-128", "intel-256", "intel-512",
]

"""Classe que representa um registro da saída do sacct.
Exemplos de linhas do sacct:
    1812139|intel-128|2026-05-05T11:36:31|2026-05-05T11:36:31|2026-05-05T12:00:13
1812140|gpu-8-v100|2026-05-05T11:37:08|2026-05-05T11:37:10|2026-05-05T11:40:46
1812155|intel-128|2026-05-05T12:13:10|2026-05-05T12:13:10|2026-05-05T12:36:29
    """
class SacctRecord:
    def __init__(self, job_id, partition, submit, start, end):
        self.job_id = job_id
        self.partition = partition
        self.submit = parse_datetime(submit)
        self.start = parse_datetime(start)
        self.end = parse_datetime(end)

"""Classe que representa um registro processado e pronto para ser salvo no JSON
de saída.
Exemplos de registros de saída:
    {"ano": 2025, "mes": 7, "particao": "intel-128", "jobs": 2342, "media_espera_segundos": 13765, "media_espera_formatado": "3h 49m 25s", "media_execucao_segundos": 24207, "media_execucao_formatado": "6h 43m 27s"}
,
{"ano": 2025, "mes": 7, "particao": "intel-256", "jobs": 755, "media_espera_segundos": 25599, "media_espera_formatado": "7h 6m 39s", "media_execucao_segundos": 17950, "media_execucao_formatado": "4h 59m 10s"}
,
{"ano": 2025, "mes": 7, "particao": "intel-512", "jobs": 1993, "media_espera_segundos": 21912, "media_espera_formatado": "6h 5m 12s", "media_execucao_segundos": 9549, "media_execucao_formatado": "2h 39m 9s"}
    """
class OcupacaoRecord:
    def __init__(self, ano, mes, particao, jobs, media_espera_segundos, media_execucao_segundos):
        self.ano = ano
        self.mes = mes
        self.particao = particao
        """Total de jobs na partição e mês"""
        self.jobs = jobs
        """Tempo médio desde a submissão até o início da execução, em segundos, 
        para todo job que foi submetido no mês e partição correspondentes."""
        self.media_espera_segundos = media_espera_segundos
        self.media_espera_formatado = format_seconds(media_espera_segundos)
        """Tempo médio desde o início da execução até o término, em segundos,
        para todo job que iniciou a execução no mês e partição correspondentes.
        """
        self.media_execucao_segundos = media_execucao_segundos
        self.media_execucao_formatado = format_seconds(media_execucao_segundos)
        self.espera_count = 0
        self.execucao_count = 0
        self.espera_total = 0
        self.execucao_total = 0

def format_seconds(segundos):
    """Formata segundos como string legível: 'Xd Yh Zm Ws'"""
    if segundos == 0:
        return "0s"
    total = int(segundos)
    dias = total // 86400
    resto = total % 86400
    horas = resto // 3600
    resto = resto % 3600
    minutos = resto // 60
    segundos_restantes = resto % 60

    partes = []
    if dias > 0:
        partes.append(f"{dias}d")
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}m")
    if segundos_restantes > 0:
        partes.append(f"{segundos_restantes}s")

    if not partes:
        return "0s"
    return " ".join(partes)


def parse_datetime(dt_str):
    """Parse datetime string from sacct output."""
    # Remove timezone info like " UTC"
    dt_str = dt_str.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None

def calcular_datas_inicio_fim(hoje)
    """Recebe a data de hoje e retorna duas datas, de inicio e fim.
    Sejam mh o mês atual, ya o ano atual e yp o ano anterior.
    Então a data de início é 1/mh/yp e a data de fim é 1/mh/ya.
    """
    mh = hoje.month
    ya = hoje.year
    yp = ya - 1
    data_inicio = datetime(yp, mh, 1)
    data_fim = datetime(ya, mh, 1)
    return data_inicio, data_fim

def executar_comando_sacct(data_inicio, data_fim):
    """Executa o comando sacct com as datas de inicio e fim fornecidas.
    Retorna a saída como uma lista de objetos SacctRecord.
    """
    CMD=[
        "sacct",
        "-X",
        "-P",
        "-S", data_inicio.strftime("%Y-%m-%d"),
        "-E", data_fim.strftime("%Y-%m-%d"),
        "--format=JobID,Partition,Submit,Start,end",
        "--noheader"
    ]
    try:        
        resultado = subprocess.run(CMD, capture_output=True, text=True, check=True)
        linhas = resultado.stdout.strip().split("\n")
        registros = []
        for linha in linhas:
            partes = linha.split("|")
            if len(partes) != 5:
                continue
            job_id, partition, submit, start, end = partes
            job_id = int(job_id)
            registros.append(SacctRecord(job_id, partition, submit, start, end))
        return registros
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar sacct: {e}", file=sys.stderr)
        return []

def processar_registros_sacct(registros):
    """Processa a lista de SacctRecord e retorna uma lista de OcupacaoRecord
    com as estatísticas calculadas.
    """
    # Estrutura para acumular dados por (ano, mes, particao)
    dados = defaultdict(lambda: OcupacaoRecord(0, 0, "", 0, 0, 0))

    for rec in registros:
        if rec.partition not in PARTICOES:
            continue
        if rec.submit is None:
            continue
        ano = rec.submit.year
        mes = rec.submit.month
        chave = (ano, mes, rec.partition)
        if chave not in dados:
            dados[chave] = OcupacaoRecord(ano, mes, rec.partition, 0, 0, 0)
        record = dados[chave]
        record.jobs += 1
        if rec.start and rec.submit:
            espera = (rec.start - rec.submit).total_seconds()
            record.espera_total += espera
            record.espera_count += 1
        if rec.end and rec.start:
            execucao = (rec.end - rec.start).total_seconds()
            record.execucao_total += execucao
            record.execucao_count += 1

    # Calcular médias
    for record in dados.values():
        if record.espera_count > 0:
            record.media_espera_segundos = record.espera_total / record.espera_count
        else:
            record.media_espera_segundos = 0
        if record.execucao_count > 0:
            record.media_execucao_segundos = record.execucao_total / record.execucao_count
        else:
            record.media_execucao_segundos = 0

    return list(dados.values())
    
def json_serializar(record):
    """Serializa um OcupacaoRecord para JSON."""
    return {
        "ano": record.ano,
        "mes": record.mes,
        "particao": record.particao,
        "jobs": record.jobs,
        "media_espera_segundos": record.media_espera_segundos,
        "media_espera_formatado": record.media_espera_formatado,
        "media_execucao_segundos": record.media_execucao_segundos,
        "media_execucao_formatado": record.media_execucao_formatado
    }

def json_serializar_lista(records):
    """Serializa uma lista de OcupacaoRecord para JSON."""
    return [json_serializar(record) for record in records]
    

def main():
    hoje = datetime.now()
    data_inicio, data_fim = calcular_datas_inicio_fim(hoje)
    registros_sacct = executar_comando_sacct(data_inicio, data_fim)
    ocupacao_records = processar_registros_sacct(registros_sacct)
    json_output = json.dumps(json_serializar_lista(ocupacao_records), indent=4)
    print(json_output)

if __name__ == "__main__":
    main()
