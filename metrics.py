#!/usr/bin/env python3

import subprocess
import json
import datetime
import sys

def round_to_100(values):
    int_parts = [int(v) for v in values]
    remainders = [(values[i] - int_parts[i], i) for i in range(len(values))]
    remainders.sort(key=lambda x: x[0], reverse=True)

    diff = 100 - sum(int_parts)

    for i in range(diff):
        category_index = remainders[i][1]
        int_parts[category_index] += 1

    return int_parts

def fetch_report(start_date, end_date):
    start_str = start_date.strftime('%m/%d/%y')
    end_str = end_date.strftime('%m/%d/%y')

    cmd_list = [
        "sreport", "cluster", "utilization",
        "start=" + start_str,
        "end=" + end_str,
        "-t", "percent",
        "-T", "cpu",
        "-nP"
    ]

    try:
        result = subprocess.run(
            cmd_list,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        output = result.stdout.decode('utf-8').strip()
        lines = output.split('\n')

        month_report = {"mes": start_date.strftime('%m-%Y')}

        if not lines or all(not line.strip() for line in lines):
            print("Warning: No data returned for {}. Skipping.".format(start_date.strftime('%m-%Y')), file=sys.stderr)
            return None

        for line in lines:
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) < 7:
                continue

            tres_name = parts[1].strip()
            json_key = ""

            if tres_name == "cpu":
                json_key = "cpu"
            else:
                continue

            allocated = float(parts[2].replace('%', ''))
            down      = float(parts[3].replace('%', ''))
            plnd_dow  = float(parts[4].replace('%', ''))
            idle      = float(parts[5].replace('%', ''))
            planned   = float(parts[6].replace('%', ''))

            used_f = allocated + planned
            idle_f = idle
            down_f = down + plnd_dow

            used, idle_val, down_val = round_to_100([used_f, idle_f, down_f])

            month_report[json_key] = {
                "utilizado": used,
                "ocioso": idle_val,
                "inativo": down_val
            }

        if len(month_report.keys()) == 1:
            print("Warning: No TRES data (cpu) found for {}. Skipping.".format(start_date.strftime('%m-%Y')), file=sys.stderr)
            return None

        return month_report

    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8')
        print("Error executing sreport for {} - {}: {}".format(start_str, end_str, error_output), file=sys.stderr)
        return None
    except Exception as e:
        print("Error parsing data for {} - {}: {}".format(start_str, end_str, e), file=sys.stderr)
        return None

def main():
    print("Iniciando coleta de dados de utilização dos últimos 12 meses...")

    today = datetime.date(2025, 11, 6)
    current_date = today.replace(day=1) - datetime.timedelta(days=1)

    reports = []

    for _ in range(12):
        start_of_month = current_date.replace(day=1)
        end_of_month = current_date

        report_data = fetch_report(start_of_month, end_of_month)
        if report_data:
            reports.append(report_data)

        current_date = start_of_month - datetime.timedelta(days=1)

    reports.reverse()

    output_filename = "utilizacao_cpu_cluster.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)

    print("Relatório salvo com sucesso em: {}".format(output_filename))

if __name__ == "__main__":
    main()
