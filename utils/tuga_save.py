# --------------------------------------------------------------------------------------------------
# TugaRecon – Módulo de Persistência e Output
# File: utils/tuga_save.py
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# --------------------------------------------------------------------------------------------------

import os        # Manipulação de caminhos e diretórios
import time      # Para medir tempos de execução
import datetime  # Para gerar datas e timestamps

# Cores para output em CLI
from utils.tuga_colors import G, Y, R, W

# Funções utilitárias
from utils.tuga_functions import print_semantic_results_grouped
from utils.impact_engine import apply_impact_engine  # Ajuste heurístico ofensivo

# Módulos de IA
from modules.IA.semantic import classify            # Classificação semântica de subdomínios
from modules.IA.impact_score import compute_impact_score  # Score técnico de impacto
from modules.IA.scan_diff_view import print_scan_diff     # Diferença visual entre scans

# Exportação de resultados
from utils.tuga_exporters import export_json, export_priority_lists

# Diferenças temporais
from utils.tuga_scan_diff import diff_scans, export_diff, get_previous_scan_date

# Ajustes de contexto
from utils.context_engine import apply_context_adjustment


# --------------------------------------------------------------------------------------------------
def _ensure_folder(path: str):
    """
    Garante que o diretório fornecido existe.
    Cria-o se não existir. Equivalente a 'mkdir -p'.
    """
    os.makedirs(path, exist_ok=True)


# --------------------------------------------------------------------------------------------------
def write_high_value_targets(results, target):
    """
    Cria ficheiro com subdomínios/alvos de alto valor
    Baseado no score ou prioridade ("CRITICAL"/"HIGH").
    """

    date = str(datetime.datetime.now().date())               # Data atual
    base_folder = os.path.join("results", target, date)      # Diretório base
    _ensure_folder(base_folder)                               # Garante existência

    # Filtra apenas alvos com score >=40 ou prioridade crítica/alta
    high_value = [
        r for r in results
        if r.get("impact_score", 0) >= 40
        or r.get("priority") in ("CRITICAL", "HIGH")
    ]

    if not high_value:  # Sai se não houver alvos relevantes
        return

    output_file = os.path.join(base_folder, "high_value_targets.txt")

    # Escreve cada alvo com formato: subdomínio, prioridade, score, tags
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
    """
    Adiciona subdomínios encontrados por brute force a um ficheiro txt.
    Cada execução adiciona linhas ao ficheiro "tuga_bruteforce.txt".
    """

    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)
    _ensure_folder(base_folder)

    output_file = os.path.join(base_folder, "tuga_bruteforce.txt")

    try:
        with open(output_file, "a", encoding="utf-8") as tmp:
            tmp.write(subdomain + "\n")  # Adiciona subdomínio ao ficheiro
    except Exception as e:
        print(R + f"[!] Failed to write bruteforce file: {e}" + W)


# --------------------------------------------------------------------------------------------------
def BruteForceReadFile(target, start_time):
    """
    Lê ficheiro de subdomínios brute force e imprime no terminal.
    Mostra contagem total e tempo gasto.
    """

    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)
    input_file = os.path.join(base_folder, "tuga_bruteforce.txt")

    if not os.path.exists(input_file):
        print(R + f"[!] No bruteforce file found for {target} on {date}" + W)
        return

    # Lê todas as linhas
    with open(input_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Mostra cada subdomínio com índice
    for index, line in enumerate(lines, start=1):
        print(f"     [*] {index}:  {line.strip()}")

    # Output resumido
    print(Y + f"\n[*] Total Subdomains Found: {len(lines)}" + W)
    print(Y + f"[**] TugaRecon: Subdomains found in {time.time() - start_time:.2f} seconds\n" + W)
    print(Y + "[+] Output Result" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W + base_folder + "\n")


# --------------------------------------------------------------------------------------------------
def write_file(subdomain, target):
    """
    Adiciona subdomínios temporários a tmp.txt.
    Servirá de input para remoção de duplicados.
    """
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
    """
    Lê tmp.txt, remove duplicados e gera osint_subdomains.txt
    Também cria diretório com data e limpa tmp.txt.
    """
    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target)
    tmp_file = os.path.join(base_folder, "tmp.txt")
    output_folder = os.path.join(base_folder, date)
    _ensure_folder(output_folder)

    output_file = os.path.join(output_folder, "osint_subdomains.txt")

    if not os.path.exists(tmp_file):
        print(R + f"[!] tmp.txt not found for {target}" + W)
        return

    # Remove duplicados e espaços
    with open(tmp_file, "r", encoding="utf-8") as f:
        content = f.readlines()

    content_set = sorted(set(line.strip() for line in content if line.strip()))

    # Escreve resultado limpo
    with open(output_file, "w", encoding="utf-8") as cleandata:
        for line in content_set:
            cleandata.write(line + "\n")

    # Remove ficheiro temporário
    try:
        os.remove(tmp_file)
    except OSError:
        pass


# --------------------------------------------------------------------------------------------------
def ReadFile(target, start_time):
    """
    Função central de processamento:
    - Lê subdomínios do ficheiro osint_subdomains.txt
    - Aplica classificação semântica e scoring de impacto
    - Propaga impacto global
    - Infere attack paths
    - Calcula worst-case
    - Persiste outputs (JSON, TXT, diffs)
    - Mostra resumo no terminal
    """

    import os
    import time
    import datetime

    from utils.impact_graph import build_impact_graph, propagate_impact
    from modules.Intelligence.attack_state import derive_attack_state
    from modules.Intelligence.attack_paths import infer_attack_paths

    from utils.tuga_attack_paths import save_attack_paths, generate_attack_path_summary
    from utils.tuga_worst_case import compute_worst_case, save_worst_case

    date = str(datetime.datetime.now().date())
    base_folder = os.path.join("results", target, date)

    attack_surface_dir = os.path.join(base_folder)

    _ensure_folder(base_folder)
    _ensure_folder(attack_surface_dir)

    subdomains_path = os.path.join(base_folder, "osint_subdomains.txt")
    if not os.path.exists(subdomains_path):
        print(R + f"[!] No subdomains file found for {target} on {date}" + W)
        return

    # ------------------------------------------------------------------
    # Lê subdomínios do ficheiro
    with open(subdomains_path, "r", encoding="utf-8") as f:
        subdomains = [line.strip() for line in f if line.strip()]

    results = []

    # ------------------------------------------------------------------
    # Classificação e scoring local
    for sub in subdomains:
        semantic = classify(sub)                    # Classifica subdomínio
        scored = compute_impact_score(semantic)    # Score técnico
        scored = apply_impact_engine(scored)       # Heurísticas ofensivas
        scored = apply_context_adjustment(scored)  # Ajuste de contexto
        scored = derive_attack_state(scored)       # Estado ofensivo final
        results.append(scored)

    # ------------------------------------------------------------------
    # Propaga impacto global na rede/target
    graph = build_impact_graph(results)
    results = propagate_impact(results, graph)

    # ------------------------------------------------------------------
    # Infere possíveis attack paths
    attack_paths = infer_attack_paths(results, graph)

    # ------------------------------------------------------------------
    # Persiste attack paths
    save_attack_paths(attack_paths, attack_surface_dir)
    generate_attack_path_summary(attack_paths, attack_surface_dir)

    # ------------------------------------------------------------------
    # Calcula pior cenário (worst-case)
    worst_case = compute_worst_case(attack_paths)
    save_worst_case(worst_case, attack_surface_dir)

    # ------------------------------------------------------------------
    # Mostra resultados no terminal de forma legível
    print_semantic_results_grouped(results)

    # ------------------------------------------------------------------
    # Exporta resultados gerais
    write_high_value_targets(results, target)
    export_json(results, target, date)
    export_priority_lists(results, target)

    # ------------------------------------------------------------------
    # Diferenças temporais entre scans
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

    # ------------------------------------------------------------------
    # Resumo final do scan
    elapsed = time.time() - start_time
    print(Y + f"[**] TugaRecon: Scan completed in {elapsed:.2f} seconds\n" + W)
    print(Y + "[+] Output directory" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W + base_folder + "\n")
