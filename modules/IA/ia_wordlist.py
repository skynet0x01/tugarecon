# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
def enrich_wordlist_from_ia(ia_subdomains, wordlist_path="wordlist/first_names.txt"):
    """
    Adiciona novos tokens à wordlist sem apagar nada
    e sem repetir entradas existentes.
    """

    # Ler wordlist existente
    try:
        with open(wordlist_path, "r") as f:
            existing = set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        existing = set()

    new_tokens = set()

    for sub in ia_subdomains:
        parts = sub.replace("-", ".").split(".")
        for p in parts:
            p = p.strip().lower()
            if len(p) < 2:
                continue
            if not p.isalnum():
                continue
            if p not in existing:
                new_tokens.add(p)

    if not new_tokens:
        print("[IA] No new tokens to add to wordlist")
        return

    # Append seguro
    with open(wordlist_path, "a") as f:
        for token in sorted(new_tokens):
            f.write(token + "\n")

    print(f"[IA] Added {len(new_tokens)} new tokens to {wordlist_path}")