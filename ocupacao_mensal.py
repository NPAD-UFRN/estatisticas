#!/usr/bin/env python3
"""
Script para gerar ocupacao_mensal.json com estatísticas de jobs do Slurm.

Gera dados para os últimos 12 meses (começando do mês anterior),
ordenados em ordem crescente.

Partições consideradas:
  amd-512, amd-3tb, gpu-4-a100, gpu-8-v100, gpu-8-h100, gpu-4-h200,
  intel-128, intel-256, intel-512

Comando Slurm usado:
  sacct - para coletar dados de jobs
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


def get_last_12_months():
    """
    Retorna lista de (ano, mes) dos últimos 12 meses,
    começando do mês anterior, em ordem crescente.
    """
    agora = datetime.now()
    # Calcular o mês anterior
    if agora.month == 1:
        mes_referencia = 12
        ano_referencia = agora.year - 1
    else:
        mes_referencia = agora.month - 1
        ano_referencia = agora.year

    meses = []
    ano = ano_referencia
    mes = mes_referencia

    for _ in range(12):
        meses.append((ano, mes))
        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

    return meses


def run_sacct(query):
    """Executa um comando sacct e retorna a saída."""
    try:
        result = subprocess.run(
            query,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"Erro ao executar sacct: {result.stderr}", file=sys.stderr)
            return []
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        print(f"Erro ao executar sacct: {e}", file=sys.stderr)
        return []


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


def query_jobs_by_month(ano, mes):
    """
    Query sacct para jobs que começaram a rodar neste mês.
    Retorna lista de dicts com job_id, start, submit, end, partition.
    """
    # Converter para string YYYY-MM-DD para o sacct
    data_inicio = f"{ano}-{mes:02d}-01"

    if mes == 12:
        data_fim = f"{ano + 1}-01-01"
    else:
        data_fim = f"{ano}-{mes + 1:02d}-01"

    # Query sacct para jobs que começaram neste mês
    query = (
        f"sacct -S {data_inicio} -E {data_fim} "
        f"-p -t COMPLETED,FAILED,CANCELLED "
        f"-n --format=JobID,Start,Submit,End,Partition "
        f"-w -a -X"
    )

    lines = run_sacct(query)

    jobs = []
    for line in lines:
        parts = line.split("|")
        if len(parts) < 5:
            continue

        job_id = parts[0].strip()
        start_str = parts[1].strip()
        submit_str = parts[2].strip()
        end_str = parts[3].strip()
        part = parts[4].strip()

        start_dt = parse_datetime(start_str)
        submit_dt = parse_datetime(submit_str)
        end_dt = parse_datetime(end_str)

        if start_dt and submit_dt and end_dt:
            wait_seconds = (start_dt - submit_dt).total_seconds()
            duration_seconds = (end_dt - start_dt).total_seconds()

            jobs.append({
                "job_id": job_id,
                "partition": part,
                "wait_seconds": wait_seconds,
                "duration_seconds": duration_seconds,
            })

    return jobs


def main():
    meses = get_last_12_months()
    resultados = []

    for ano, mes in meses:
        print(f"Processando: {ano}-{mes:02d}", file=sys.stderr)

        jobs = query_jobs_by_month(ano, mes)

        # Agrupar por partição
        por_particao = defaultdict(list)
        for job in jobs:
            por_particao[job["partition"]].append(job)

        for particao in PARTICOES:
            jobs_da_particao = por_particao.get(particao, [])

            if not jobs_da_particao:
                continue

            jobs_count = len(jobs_da_particao)
            wait_times = [j["wait_seconds"] for j in jobs_da_particao]
            durations = [j["duration_seconds"] for j in jobs_da_particao]

            avg_wait = sum(wait_times) / len(wait_times)
            avg_duration = sum(durations) / len(durations)

            avg_wait_int = int(round(avg_wait))
            avg_duration_int = int(round(avg_duration))

            entry = {
                "ano": ano,
                "mes": mes,
                "particao": particao,
                "jobs": jobs_count,
                "media_espera_segundos": avg_wait_int,
                "media_espera_formatado": format_seconds(avg_wait_int),
                "media_execucao_segundos": avg_duration_int,
                "media_execucao_formatado": format_seconds(avg_duration_int),
            }
            resultados.append(entry)

    # Ordenar por ano, mes, particao
    resultados.sort(key=lambda x: (x["ano"], x["mes"], x["particao"]))

    # Escrever JSON na saída padrão
    print(json.dumps(resultados, indent=None))


if __name__ == "__main__":
    main()
