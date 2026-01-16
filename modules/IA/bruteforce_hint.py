# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

COMMON_SERVICE_HINTS = {
    "admin": ["console", "panel", "dashboard", "manage"],
    "auth": ["sso", "login", "oauth", "keycloak"],
    "api": ["api-v1", "api-v2", "graphql", "internal-api"],
    "internal": ["vpn", "intranet", "corp", "lan"],
}

def generate_hints(semantic_results):
    hints = set()

    for r in semantic_results:
        tags = r.get("tags", [])
        for t in tags:
            for h in COMMON_SERVICE_HINTS.get(t, []):
                hints.add(h)

    return sorted(hints)
