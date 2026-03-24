# --------------------------------------------------------------------------------------------------
# TugaRecon – CLI Orchestrator (Refactored)
# File: tugarecon.py
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import os              # Fornece funções para interagir com o sistema operativo (ficheiros, diretórios, variáveis de ambiente, etc.)
import sys             # Permite interagir com o interpretador Python (argumentos da linha de comandos, saída do programa, etc.)
import time            # Funções relacionadas com tempo (pausas com sleep, medir tempo de execução, timestamps simples)
import argparse        # Facilita a criação de interfaces de linha de comandos (parse de argumentos tipo --input, --output, etc.)
import logging         # Sistema de logging para registar eventos, erros e informação (debug, info, warning, error)

# Permite trabalhar com datas e horas (obter data atual, formatar timestamps, etc.)
from datetime import datetime

# dataclass: cria classes mais simples para armazenar dados (menos código boilerplate)
# field: permite configurar campos da dataclass (valores default, listas, etc.)
from dataclasses import dataclass, field

# Forma moderna e mais limpa de trabalhar com caminhos de ficheiros e diretórios (substitui muitas vezes o os.path)
from pathlib import Path

from utils.tuga_colors import G, W, R, Y
from utils.tuga_dns import bscan_whois_look
from utils.tuga_results import main_work_subdirs
from utils.tuga_save import ReadFile, DeleteDuplicate

from modules.IA.trainer import run_ia_training

from modules.Brute_Force.tuga_probe import TugaServiceProbe

from modules.Intelligence.unified_engine import process_entry
from modules.Intelligence.tuga_attack_surface import TugaAttackSurface

# --------------------------------------------------------------------------------------------------
# Logging global da aplicação
# --------------------------------------------------------------------------------------------------
# Define formato simples e nível default INFO
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger(" tugarecon")


# --------------------------------------------------------------------------------------------------
# Scan Context
# --------------------------------------------------------------------------------------------------
# Estrutura que mantém o estado da execução.
# Evita passar múltiplos parâmetros entre funções.
# --------------------------------------------------------------------------------------------------
@dataclass
class ScanContext:
    target: str
    enum: list | None
    bruteforce: bool
    threads: int
    savemap: bool
    args: argparse.Namespace

    start_time: float = field(default_factory=time.time)
    semantic_hints: list = field(default_factory=list)

    @property
    def scan_dir(self) -> str:
        return f"results/{self.target}/{datetime.now().date()}"


# --------------------------------------------------------------------------------------------------
# CLI Argument Parsing
# --------------------------------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    Examples = (Y + '''
    ────────────────────────────────────────────────────────────
     Available Modules:
    ────────────────────────────────────────────────────────────
      • OSINT      • Brute-Force      • IA      • Intelligence
      • Network-map                   • And much more...
    ────────────────────────────────────────────────────────────
     Examples of Usage:
    ────────────────────────────────────────────────────────────
      ▶ Enumerate all modules (except bruteforce):
          python3 tugarecon.py -d google.com

      ▶ Bruteforce subdomains using wordlists:
          python3 tugarecon.py -d google.com -b

      ▶ View saved results:
          python3 tugarecon.py -r

      ▶ Generate network graph (with ASN clusters):
          python3 tugarecon.py -d google.com -m

    ────────────────────────────────────────────────────────────
     Donations are welcome ♥
     Help improve features, updates, and support:
     → https://github.com/skynet0x01/tugarecon
    ────────────────────────────────────────────────────────────
    ''' + W)

    parser = argparse.ArgumentParser(
        epilog=Examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-d', '--domain', help='Target domain')
    parser.add_argument('-e', '--enum', nargs='*', help='Select OSINT modules')
    parser.add_argument('-b', '--bruteforce', action='store_true', help='Enable bruteforce')
    parser.add_argument('-t', '--threads', type=int, default=250)
    parser.add_argument('-m', '--map', action='store_true', help='Generate network map')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    parser.add_argument("-r", "--results", action="store_true", help="Show previously saved scan results and exit")
    #parser.add_argument("--report", action="store_true", help="Generate intelligence report after scan")
    #parser.add_argument("--pdf", action="store_true", help="Generate report in PDF format")

    return parser.parse_args()


# --------------------------------------------------------------------------------------------------
# PIPELINES
# Cada função abaixo executa uma fase do scan.
# --------------------------------------------------------------------------------------------------
def run_bruteforce(ctx: ScanContext) -> None:
    log.info(
        " Running brute force module")
    log.info(
        " Brute force in progress... this may take some time! ")

    from modules.Brute_Force.tuga_bruteforce import TugaBruteForce
    from modules.IA.bruteforce_hint import generate_hints

    if hasattr(ctx.args, "semantic_results") and ctx.args.semantic_results:
        ctx.semantic_hints = generate_hints(ctx.args.semantic_results)
        log.info(f" Generated {len(ctx.semantic_hints)} IA hints")

    options = {"target": ctx.target, "threads": ctx.threads, "semantic_hints": ctx.semantic_hints}
    TugaBruteForce(options=options).run()


def run_map(ctx: ScanContext) -> None:
    log.info(" Generating network map")
    from modules.Map.tuga_network_map import tuga_map
    tuga_map(ctx.target)


def run_enumeration(ctx: ScanContext) -> None:
    """
        Executa todos os módulos OSINT configurados.
    """
    log.info(" Starting OSINT enumeration")

    from progress.bar import IncrementalBar
    from modules.OSINT.tuga_modules import queries
    from modules.OSINT import (
        tuga_sublist3r, tuga_threatcrowd, tuga_crt, tuga_threatminer,
        tuga_certspotter, tuga_dnsdumpster, tuga_alienvault, tuga_hackertarget,
        tuga_omnisint, tuga_dnsbufferover, tuga_rapiddns,
    )

    # Mapeamento nome → classe engine
    engines = {
        'certspotter': tuga_certspotter.Certspotter,
        'ssl': tuga_crt.CRT,
        'hackertarget': tuga_hackertarget.Hackertarget,
        'threatcrowd': tuga_threatcrowd.Threatcrowd,
        'alienvault': tuga_alienvault.Alienvault,
        'threatminer': tuga_threatminer.Threatminer,
        'omnisint': tuga_omnisint.Omnisint,
        'sublist3r': tuga_sublist3r.Sublist3r,
        'dnsdumpster': tuga_dnsdumpster.DNSDUMPSTER,
        'dnsbufferover': tuga_dnsbufferover.DNSBufferOver,
        'rapiddns': tuga_rapiddns.RapidDNS,
    }

    selected = engines.values() if ctx.enum is None else [engines[e] for e in ctx.enum if e in engines]

    queries(ctx.target)
    bar = IncrementalBar('OSINT', max=len(selected))

    for engine in selected:
        engine(ctx.target)
        bar.next()

    bar.finish()

    DeleteDuplicate(ctx.target)
    ReadFile(ctx.target, ctx.start_time)

    # IA learning from OSINT results
    run_ia_training(ctx.target)


# --------------------------------------------------------------------------------------------------
def run_probe(ctx: ScanContext) -> None:
    print("")
    log.info(" Running service probe module")
    print("")

    scan_dir = ctx.scan_dir
    osint_hosts = os.path.join(scan_dir, "osint_subdomains.txt")
    brute_hosts = os.path.join(scan_dir, "tuga_bruteforce.txt")

    input_file = osint_hosts if os.path.isfile(osint_hosts) else brute_hosts if os.path.isfile(brute_hosts) else None
    if not input_file:
        log.warning(" No hosts file found for probe phase")
        return

    output_dir = os.path.join(scan_dir, "probe")
    probe = TugaServiceProbe(input_file=input_file, output_dir=output_dir, concurrency=80, timeout=6, verbose=False)
    probe.run()


# --------------------------------------------------------------------------------------------------
def run_context(ctx: ScanContext) -> None:
    print("")
    log.info(" Building scan context")

    from modules.Brute_Force.tuga_context import TugaContext

    services_file = os.path.join(ctx.scan_dir, "probe", "services.json")

    if not os.path.isfile(services_file):
        log.warning("services.json not found, skipping context module")
        return

    # escolher fonte de subdomínios
    brutefile = os.path.join(ctx.scan_dir, "tuga_bruteforce.txt")
    osintfile = os.path.join(ctx.scan_dir, "osint_subdomains.txt")

    if os.path.isfile(brutefile):
        subdomains_file = brutefile
        log.info(" Using brute-force subdomains for context, (processing brute force list, please wait)...")
    elif os.path.isfile(osintfile):
        subdomains_file = osintfile
        log.info(" Using OSINT subdomains for context")
        print("")
    else:
        print("")
        log.warning(" No subdomains file found for context, skipping")
        return

    # definir output_dir AQUI (antes de usar)
    output_dir = os.path.join(ctx.scan_dir, "context")

    context = TugaContext(
        bruteforce_file=subdomains_file,
        services_file=services_file,
        output_dir=output_dir
    )

    context.run()
# --------------------------------------------------------------------------------------------------
def run_attack_surface(ctx: ScanContext) -> None:
    print("")
    log.info(" Building attack surface")

    context_file = os.path.join(ctx.scan_dir, "context", "context.json")
    output_dir = os.path.join(ctx.scan_dir, "attack_surface")

    if not os.path.isfile(context_file):
        log.warning("Context file not found, skipping attack surface")
        return

    attack = TugaAttackSurface(context_file, output_dir)
    attack.run()


# --------------------------------------------------------------------------------------------------
def run_intelligence(ctx: ScanContext) -> None:
    import os
    import json
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from utils.temporal_analysis import analyze_temporal_state
    from utils.temporal_score import compute_temporal_score
    from utils.temporal_view import print_top_temporal
    from modules.Intelligence.snapshot import (
        load_previous_snapshot,
        build_snapshot,
        save_snapshot
    )

    print("")
    log.info(" Running temporal intelligence analysis (processing historical deltas, please wait)...")

    semantic_file = os.path.join(ctx.scan_dir, "semantic_results.json")
    if not os.path.isfile(semantic_file):
        log.warning(" Semantic results not found, skipping intelligence module")
        return

    previous = load_previous_snapshot(ctx.scan_dir)

    with open(semantic_file, "r") as f:
        results = json.load(f)

    snapshot = build_snapshot(results, previous)
    save_snapshot(ctx.scan_dir, snapshot)

    # Normalizar last_seen para YYYY-MM-DD
    for sub, data in snapshot.get("subdomains", {}).items():
        last_seen = data.get("last_seen")
        if isinstance(last_seen, str):
            try:
                parsed = datetime.fromisoformat(last_seen)
                data["last_seen"] = parsed.date().isoformat()
            except ValueError:
                pass

    states = analyze_temporal_state(snapshot, previous)

    ranking = []
    output_dir = os.path.join(ctx.scan_dir, "reactions")
    os.makedirs(output_dir, exist_ok=True)

    def process_sub(state, sub):
        data = snapshot["subdomains"].get(sub, {})
        temporal_score = compute_temporal_score(data, state)

        if data.get("impact_score", 0) > 0 or state == "NEW":
            action = "REVIEW"
        else:
            action = "IGNORE"

        entry = {
            "subdomain": sub,
            "state": state,
            "temporal_score": temporal_score,
            "impact_score": data.get("impact_score", 0),
            "tags": data.get("tags", []),
            "action": action
        }

        process_entry(entry, output_dir)

        return {
            "subdomain": sub,
            "state": state,
            "score": temporal_score,
            "impact": data.get("impact_score", 0),
            "action": action
        }

    futures = []

    # Ajuste do max_workers conforme a máquina (16 é equilibrado para I/O)
    with ThreadPoolExecutor(max_workers=16) as executor:
        for state, subs in states.items():
            for sub in subs:
                futures.append(executor.submit(process_sub, state, sub))

        for future in as_completed(futures):
            ranking.append(future.result())

    ranking.sort(key=lambda x: x["score"], reverse=True)

    has_actionable = any(entry["action"] != "IGNORE" for entry in ranking)

    print("\n──────────────────────────────────────────────────────────────────────")
    print("[🧠] Temporal Risk View – Top Targets")
    print("──────────────────────────────────────────────────────────────────────")

    if not has_actionable:
        print("✓ No actionable temporal risk detected")
    else:
        print_top_temporal(ranking)

    print("──────────────────────────────────────────────────────────────────────")

# --------------------------------------------------------------------------------------------------
# START PIPELINE
# --------------------------------------------------------------------------------------------------
def start(ctx: ScanContext) -> None:
    """
        Define ordem de execução dos módulos.
    """

    # Informação WHOIS inicial
    bscan_whois_look(ctx.target)

    # Fluxo exclusivo bruteforce
    if ctx.bruteforce:
        run_bruteforce(ctx)
        run_probe(ctx)
        run_context(ctx)
        run_attack_surface(ctx)
        return

    # Apenas o mapa
    if ctx.savemap:
        return run_map(ctx)

    # Fluxo completo
    run_enumeration(ctx)
    run_probe(ctx)
    run_context(ctx)
    run_attack_surface(ctx)
    run_intelligence(ctx)


# --------------------------------------------------------------------------------------------------
# MAIN ENTRYPOINT
# --------------------------------------------------------------------------------------------------
def main() -> None:
    from utils.tuga_banner import banner

    banner()
    args = parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    if args.results:
        main_work_subdirs()
        return

    if not args.domain:
        print(R + "[!] You must specify a domain unless using -r/--results" + W)
        sys.exit(1)

    ctx = ScanContext(
        target=args.domain,
        enum=args.enum,
        bruteforce=args.bruteforce,
        threads=args.threads,
        savemap=args.map,
        args=args
    )

    try:
        start(ctx)
    except KeyboardInterrupt:
        print(G + "\nTugaRecon interrupted by user" + W)
        sys.exit(130)

    # --------------------------------------------------------------------------------------------------
    # Relatórios automáticos (Markdown + PDF)
    # --------------------------------------------------------------------------------------------------
    from utils.tugarecon_report import generate_report

    report_dir = Path(ctx.scan_dir) / "report"
    report_dir.mkdir(parents=True, exist_ok=True)  # garante apenas uma pasta

    # Chama função de geração de relatório diretamente
    md_file, pdf_file = generate_report(report_dir, generate_pdf=True)

    print(f"[📄] Markdown report generated: {md_file}")
    print(f"[📕] PDF report generated: {pdf_file}")

if __name__ == '__main__':
    main()