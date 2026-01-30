import os

def generate_attack_path_summary(attack_paths, base_dir):
    """
    Generates a human-readable summary of attack paths.
    """

    out_dir = os.path.join(base_dir, "attack_surface")
    os.makedirs(out_dir, exist_ok=True)

    path = os.path.join(out_dir, "attack_path_summary.txt")

    if not attack_paths:
        with open(path, "w") as f:
            f.write("No plausible attack paths identified.\n")
        return path

    with open(path, "w") as f:
        f.write("=== TugaRecon – Plausible Attack Paths ===\n\n")

        for i, ap in enumerate(attack_paths, 1):
            f.write(f"[PATH {i}]\n")
            f.write(" → ".join(ap["path"]) + "\n")
            f.write(f"Total Cost   : {ap['total_cost']}\n")
            f.write(f"Final Impact : {ap['final_impact']}\n")
            f.write(f"Confidence   : {ap['confidence']}\n")
            f.write("\n")

    return path
