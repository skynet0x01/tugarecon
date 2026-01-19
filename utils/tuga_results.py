# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
"""
tuga_results.py

Responsabilidade:
- Explorar a árvore de resultados do TugaRecon
- Agregar informação por domínio e data
- Fornecer uma visão humana do histórico de scans
- Servir como base para dashboards, timelines e relatórios

Este módulo NÃO faz análise semântica nem scoring.
Ele apenas organiza e apresenta o que os outros módulos produziram.
"""

import os
import json
from typing import Dict, List

from utils.tuga_colors import G, Y, B, R, W

# --------------------------------------------------------------------------------------------------
ROOTDIR = "results"

# --------------------------------------------------------------------------------------------------
def show_saved_results(domain_filter=None, only_last=False):
    """
    Mostra os resultados guardados, opcionalmente filtrando por domínio ou mostrando só o último scan.
    """
    if not os.path.isdir(ROOTDIR):
        print(R + "[!] No results directory found." + W)
        return

    print("\nResults:")
    print(G + "────────────────────────────────────────────────────────────" + W)

    domains = sorted(d for d in os.listdir(ROOTDIR)
                     if os.path.isdir(os.path.join(ROOTDIR, d)))

    if domain_filter:
        domains = [d for d in domains if d.lower() == domain_filter.lower()]
        if not domains:
            print(R + f"[!] No results found for domain: {domain_filter}" + W)
            return

    for domain in domains:
        domain_path = os.path.join(ROOTDIR, domain)
        scans = sorted(
            d for d in os.listdir(domain_path)
            if os.path.isdir(os.path.join(domain_path, d))
        )

        if not scans:
            continue

        if only_last:
            scans = [scans[-1]]

        print(Y + f"[Domain] {domain}" + W)

        for scan_date in scans:
            summary_file = os.path.join(domain_path, scan_date, "summary.txt")
            if not os.path.isfile(summary_file):
                # Se não existir summary.txt, tenta gerar pelo semantic_results.json
                summary_data = summarize_scan(domain, scan_date)
                print(
                    B + f"  └─ {scan_date}  "
                    f"total={summary_data['total']:>4}  "
                    f"C={summary_data['CRITICAL']:>3}  "
                    f"H={summary_data['HIGH']:>3}  "
                    f"M={summary_data['MEDIUM']:>3}  "
                    f"L={summary_data['LOW']:>3}"
                    + W
                )
                continue

            with open(summary_file, "r", encoding="utf-8", errors="ignore") as f:
                line = f.read().strip()

            print(f"  └─ {scan_date}  {line}")

    print("\nLegend: C=CRITICAL  H=HIGH  M=MEDIUM  L=LOW")
    print(G + "────────────────────────────────────────────────────────────" + W)


# --------------------------------------------------------------------------------------------------
def list_domains(rootdir: str = "results") -> List[str]:
    """
    Lista todos os domínios existentes em results/.
    """
    if not os.path.exists(rootdir):
        return []

    return sorted(
        d for d in os.listdir(rootdir)
        if os.path.isdir(os.path.join(rootdir, d))
    )


# --------------------------------------------------------------------------------------------------
def list_scans_for_domain(domain: str, rootdir: str = "results") -> List[str]:
    """
    Lista todas as datas de scan para um domínio.
    """
    base = os.path.join(rootdir, domain)
    if not os.path.exists(base):
        return []

    return sorted(
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d))
    )


# --------------------------------------------------------------------------------------------------
def load_semantic_results(domain: str, date: str,
                          rootdir: str = "results") -> List[dict]:
    """
    Carrega semantic_results.json para um domínio/data.
    """
    path = os.path.join(rootdir, domain, date, "semantic_results.json")
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# --------------------------------------------------------------------------------------------------
def summarize_scan(domain: str, date: str,
                   rootdir: str = "results") -> Dict[str, int]:
    """
    Produz um pequeno resumo estatístico de um scan.
    """
    results = load_semantic_results(domain, date, rootdir)

    summary = {
        "total": len(results),
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for r in results:
        p = r.get("priority", "LOW")
        if p in summary:
            summary[p] += 1

    return summary


# --------------------------------------------------------------------------------------------------
def print_results_tree(domain_filter=None, only_last=False, rootdir: str = "results"):
    """
    Imprime a árvore de resultados com resumos por scan, com suporte a filtro e só último scan.
    """
    domains = list_domains(rootdir)

    if domain_filter:
        domains = [d for d in domains if d.lower() == domain_filter.lower()]
        if not domains:
            print(R + f"[!] No results found for domain: {domain_filter}" + W)
            return

    if not domains:
        print(R + "[!] No results found" + W)
        return

    print("\nResults:")
    print(G + "────────────────────────────────────────────────────────────" + W)

    for domain in domains:
        print(Y + f"[Domain] {domain}" + W)

        scans = list_scans_for_domain(domain, rootdir)
        if only_last and scans:
            scans = [scans[-1]]

        for date in scans:
            summary = summarize_scan(domain, date, rootdir)

            print(
                B + f"  └─ {date}  "
                f"total={summary['total']:>4}  "
                f"C={summary['CRITICAL']:>3}  "
                f"H={summary['HIGH']:>3}  "
                f"M={summary['MEDIUM']:>3}  "
                f"L={summary['LOW']:>3}"
                + W
            )

    print("\nLegend: C=CRITICAL  H=HIGH  M=MEDIUM  L=LOW")
    print(G + "────────────────────────────────────────────────────────────" + W)


# --------------------------------------------------------------------------------------------------
def main_work_subdirs(domain_filter=None, only_last=False):
    """
    Função legacy compatível com a versão original.
    Agora delega para print_results_tree(), com suporte a filtros.
    """
    print_results_tree(domain_filter=domain_filter, only_last=only_last)
