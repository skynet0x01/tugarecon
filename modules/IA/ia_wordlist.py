# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# Module: modules/IA/ia_wordlist.py
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

def enrich_wordlist_from_ia(ia_subdomains, wordlist_path="wordlist/first_names.txt"):
    """
    Adiciona novos tokens à wordlist sem apagar nada
    e sem repetir entradas existentes.

    Parâmetros:
    - ia_subdomains: lista de subdomínios gerados por IA (ex: ["api-dev.example.com"])
    - wordlist_path: caminho para a wordlist que será enriquecida

    Filosofia do método:
    - Nunca remover entradas existentes
    - Nunca duplicar tokens
    - Apenas acrescentar novos termos relevantes
    """

    # ------------------------------------------------------------
    # 1) Carregar wordlist existente para memória
    # ------------------------------------------------------------
    # Usamos um set() porque:
    # - Evita duplicados automaticamente
    # - Permite pesquisa O(1) (extremamente eficiente)
    # - Garante normalização consistente
    try:
        with open(wordlist_path, "r") as f:
            # Strip remove espaços e \n
            # lower() garante consistência (evita "Admin" != "admin")
            # Ignoramos linhas vazias
            existing = set(line.strip().lower() for line in f if line.strip())

    except FileNotFoundError:
        # Se o ficheiro ainda não existir,
        # começamos com um conjunto vazio
        existing = set()

    # ------------------------------------------------------------
    # 2) Preparar estrutura para novos tokens
    # ------------------------------------------------------------
    # Outro set() para:
    # - Evitar duplicação entre novos tokens
    # - Garantir escrita limpa no final
    new_tokens = set()

    # ------------------------------------------------------------
    # 3) Processar cada subdomínio gerado pela IA
    # ------------------------------------------------------------
    for sub in ia_subdomains:

        # Normalização estrutural:
        # - Substituímos "-" por "."
        #   porque queremos dividir também palavras compostas
        #   Ex: "api-dev.example.com"
        #   torna-se: "api.dev.example.com"
        parts = sub.replace("-", ".").split(".")

        # Agora iteramos por cada segmento separado
        for p in parts:

            # Normalização de cada token
            p = p.strip().lower()

            # ----------------------------------------------------
            # Filtros de sanidade
            # ----------------------------------------------------

            # Ignorar tokens demasiado pequenos
            # Evita lixo como:
            # - "a"
            # - "1"
            # - fragmentos irrelevantes
            if len(p) < 2:
                continue

            # Garantir que o token é apenas alfanumérico
            # Evita:
            # - caracteres especiais
            # - símbolos estranhos
            # - potenciais injeções indesejadas
            if not p.isalnum():
                continue

            # ----------------------------------------------------
            # Evitar duplicados
            # ----------------------------------------------------
            # Só adicionamos se:
            # - ainda não existir na wordlist original
            # - ainda não tiver sido marcado nesta execução
            if p not in existing:
                new_tokens.add(p)

    # ------------------------------------------------------------
    # 4) Se não houver nada novo, terminamos cedo
    # ------------------------------------------------------------
    if not new_tokens:
        print("[IA] No new tokens to add to wordlist")
        return

    # ------------------------------------------------------------
    # 5) Escrita segura (append mode)
    # ------------------------------------------------------------
    # "a" significa append:
    # - nunca apaga o conteúdo existente
    # - apenas acrescenta ao final
    with open(wordlist_path, "a") as f:

        # sorted() não é obrigatório,
        # mas garante ordem determinística.
        # Isso ajuda em debugging e controlo de versões.
        for token in sorted(new_tokens):
            f.write(token + "\n")

    # Feedback informativo
    print(f"[IA] Added {len(new_tokens)} new tokens to {wordlist_path}")
