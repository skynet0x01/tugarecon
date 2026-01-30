# --------------------------------------------------------------------------------------------------
# TugaRecon
# File: utils/tuga_save.py
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import os
import time
import datetime

from utils.tuga_colors import G, Y, R, W
from utils.tuga_functions import print_semantic_results_grouped
from utils.impact_engine import apply_impact_engine # NEW

from modules.IA.semantic import classify
from modules.IA.impact_score import compute_impact_score
from modules.IA.scan_diff_view import print_scan_diff

from utils.tuga_exporters import export_json, export_priority_lists
from utils.tuga_scan_diff import diff_scans, export_diff, get_previous_scan_date
from utils.context_engine import apply_context_adjustment


# --------------------------------------------------------------------------------------------------
def _ensure_folder(path: str):
    os.makedirs(path, exist_ok=True)


# --------------------------------------------------------------------------------------------------
def write_high_value_targets(results, target):
    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)
    _ensure_folder(base_folder)

    high_value = [
        r for r in results
        if r.get("impact_score", 0) >= 40
        or r.get("priority") in ("CRITICAL", "HIGH")
    ]

    if not high_value:
        return

    output_file = os.path.join(base_folder, "high_value_targets.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        for r in high_value:
            f.write(
                f"{r['subdomain']:<50} "
                f"[{r['priority']:<8}] "
                f"score={r['impact_score']:>3} "
                f"tags={','.join(r.get('tags', []))}\n"
            )


# --------------------------------------------------------------------------------------------------
def write_file_bruteforce(subdomain, target):
    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)
    _ensure_folder(base_folder)

    output_file = os.path.join(base_folder, "tuga_bruteforce.txt")

    try:
        with open(output_file, "a", encoding="utf-8") as tmp:
            tmp.write(subdomain + "\n")
    except Exception as e:
        print(R + f"[!] Failed to write bruteforce file: {e}" + W)


# --------------------------------------------------------------------------------------------------
def BruteForceReadFile(target, start_time):
    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)
    input_file = os.path.join(base_folder, "tuga_bruteforce.txt")

    if not os.path.exists(input_file):
        print(R + f"[!] No bruteforce file found for {target} on {date}" + W)
        return

    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    for index, line in enumerate(lines, start=1):
        print(f"     [*] {index}:  {line.strip()}")

    print(Y + f"\n[*] Total Subdomains Found: {len(lines)}" + W)
    print(Y + f"[**] TugaRecon: Subdomains found in {time.time() - start_time:.2f} seconds\n" + W)
    print(Y + "[+] Output Result" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W + base_folder + "\n")


# --------------------------------------------------------------------------------------------------
def write_file(subdomain, target):
    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target)
    _ensure_folder(base_folder)

    tmp_file = os.path.join(base_folder, "tmp.txt")

    try:
        with open(tmp_file, "a", encoding="utf-8") as tmp:
            tmp.write(subdomain + "\n")
    except Exception as e:
        print(R + f"[!] Failed to write tmp file: {e}" + W)


# --------------------------------------------------------------------------------------------------
def DeleteDuplicate(target):
    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target)
    tmp_file = os.path.join(base_folder, "tmp.txt")
    output_folder = os.path.join(base_folder, date)
    _ensure_folder(output_folder)

    output_file = os.path.join(output_folder, "osint_subdomains.txt")

    if not os.path.exists(tmp_file):
        print(R + f"[!] tmp.txt not found for {target}" + W)
        return

    with open(tmp_file, "r", encoding="utf-8") as f:
        content = f.readlines()

    content_set = sorted(set(line.strip() for line in content if line.strip()))

    with open(output_file, "w", encoding="utf-8") as cleandata:
        for line in content_set:
            cleandata.write(line + "\n")

    try:
        os.remove(tmp_file)
    except OSError:
        pass


# --------------------------------------------------------------------------------------------------
def ReadFile(target, start_time):
    from utils.impact_graph import build_impact_graph, propagate_impact
    from modules.Intelligence.attack_state import derive_attack_state

    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)
    _ensure_folder(base_folder)

    subdomains_path = os.path.join(base_folder, "osint_subdomains.txt")
    if not os.path.exists(subdomains_path):
        print(R + f"[!] No subdomains file found for {target} on {date}" + W)
        return

    # Read subdomains
    with open(subdomains_path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    # Classify and compute impact scores
    results = []

    # Impact score é local.
    for s in lines:
        semantic = classify(s)

        scored = compute_impact_score(semantic)     # → impacto técnico
        scored = apply_impact_engine(scored)        # → heurísticas ofensivas (vpn, auth, admin…)
        scored = apply_context_adjustment(scored)   #  → ambiente, trust boundary, exposição
        scored = derive_attack_state(scored)        # ← AQUI (novo estado ofensivo)

        results.append(scored)

    from utils.tuga_attack_paths import save_attack_paths
    from utils.tuga_attack_path_summary import generate_attack_path_summary
    from modules.Intelligence.attack_paths import infer_attack_paths

    # Impact graph é global.
    graph = build_impact_graph(results)
    results = propagate_impact(results, graph)

    attack_paths = infer_attack_paths(results, graph)

    # Persistência (dados)
    save_attack_paths(attack_paths, base_folder)
    generate_attack_path_summary(attack_paths, base_folder)

    from utils.tuga_worst_case import compute_worst_case
    worst_case = compute_worst_case(attack_paths)

    # Print semantic results
    print_semantic_results_grouped(results)

    # Save results
    write_high_value_targets(results, target)
    export_json(results, target, date)
    export_priority_lists(results, target)

    # Compare with previous scan
    today = date
    prev_date = get_previous_scan_date(target, today)

    if prev_date:
        diff = diff_scans(target, prev_date, today)
        export_diff(diff, target, today)
        print_scan_diff(diff)
        print("")
        print(G + f"[Δ] Diff generated against {prev_date}" + W)
        print("")
    else:
        print(Y + "[Δ] No previous scan found (baseline created)" + W)

    # Summary
    elapsed = time.time() - start_time
    print(Y + f"[**] TugaRecon: Scan completed in {elapsed:.2f} seconds\n" + W)
    print(Y + "[+] Output directory" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W + base_folder + "\n")

