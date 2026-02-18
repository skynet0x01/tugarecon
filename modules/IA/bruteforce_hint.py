# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# COMMON_SERVICE_HINTS
#
# Este dicionário define relações semânticas entre tipos de serviços
# identificados durante análise (OSINT / scraping / enumeração) e possíveis
# subdomínios associados a esses serviços.
#
# Exemplo:
#   Se durante análise detectamos que o alvo usa um serviço de "auth",
#   é altamente provável que existam subdomínios como:
#       login.target.com
#       sso.target.com
#       oauth.target.com
#
# Isto permite transformar descoberta passiva em ataque dirigido.
# --------------------------------------------------------------------------------------------------

COMMON_SERVICE_HINTS = {
    "admin": ["console", "panel", "dashboard", "manage"],

    # Serviços de autenticação normalmente expõem endpoints dedicados
    "auth": ["sso", "login", "oauth", "keycloak"],

    # APIs modernas frequentemente têm versionamento explícito
    "api": ["api-v1", "api-v2", "graphql", "internal-api"],

    # Infraestrutura interna tende a ter nomes previsíveis
    "internal": ["vpn", "intranet", "corp", "lan"],
}

# --------------------------------------------------------------------------------------------------
# generate_hints
#
# Objetivo:
#   Gerar lista de subdomínios candidatos com base em resultados semânticos.
#
# Entrada:
#   semantic_results → lista de dicionários produzidos por análise anterior
#                      Exemplo:
#                      [
#                          {"tags": ["auth", "api"]},
#                          {"tags": ["admin"]}
#                      ]
#
# Processo:
#   - Percorre cada resultado
#   - Extrai tags associadas
#   - Para cada tag, verifica se existe mapeamento em COMMON_SERVICE_HINTS
#   - Adiciona sugestões correspondentes a um set (evita duplicados)
#
# Saída:
#   Lista ordenada de hints únicos
#
# Filosofia:
#   Recon orientado por contexto é exponencialmente mais eficiente
#   que brute force totalmente cego.
# --------------------------------------------------------------------------------------------------

def generate_hints(semantic_results):
    """
    Gera subdomínios candidatos com base em tags semânticas.

    Retorna lista ordenada e sem duplicados.
    """

    hints = set()  # usamos set para evitar repetição automática

    # Percorre cada resultado da camada semântica
    for r in semantic_results:

        # Obtém lista de tags associadas ao resultado
        # Se não existir chave "tags", retorna lista vazia
        tags = r.get("tags", [])

        # Para cada tag encontrada
        for t in tags:

            # Verifica se existe mapeamento no dicionário principal
            # Se não existir, retorna lista vazia
            for h in COMMON_SERVICE_HINTS.get(t, []):

                # Adiciona hint ao conjunto
                hints.add(h)

    # Retorna lista ordenada para consistência determinística
    return sorted(hints)

