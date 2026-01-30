import json
import os

def save_attack_paths(attack_paths, base_dir):
    """
    Saves inferred attack paths as pure JSON.
    """
    out_dir = os.path.join(base_dir, "attack_surface")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, "attack_paths.json")

    with open(path, "w") as f:
        json.dump(attack_paths, f, indent=2)

    return path
