# --------------------------------------------------------------------------------------------------
# TugaRecon – Worst Case Attack Path Utilities
# Author: Skynet0x01 2020-2026
# License: GNU GPLv3
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import json
import os
from typing import List, Dict, Optional


# --------------------------------------------------------------------------------------------------
def compute_worst_case(attack_paths: List[Dict]) -> Optional[Dict]:
    """
    Compute the 'worst case scenario' from a list of attack paths.

    Criteria:
      - The path with the highest final impact is considered worst.

    Args:
        attack_paths (List[Dict]): List of attack path dicts.

    Returns:
        Dict: The attack path dict representing the worst case, or None if empty.
    """
    if not attack_paths:
        return None

    # Escolhe o path com maior impacto final
    worst = max(attack_paths, key=lambda p: p.get("final_impact", 0))
    return worst


# --------------------------------------------------------------------------------------------------
def save_worst_case(worst_case: Optional[Dict], base_dir: str) -> None:
    """
    Save the worst case attack path to JSON in attack_surface folder.

    Args:
        worst_case (Dict): Worst case path dict from compute_worst_case().
        base_dir (str): Root results folder for the target scan.
    """
    if not worst_case:
        return

    folder = os.path.join(base_dir, "attack_surface")
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, "worst_case.json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(worst_case, f, indent=2)
    except Exception as e:
        print(f"[!] Failed to save worst_case.json: {e}")
