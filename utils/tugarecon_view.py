#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return None

def header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def show_priority_targets(base_dir):
    path = base_dir / "attack_surface" / "priority_targets.txt"
    header("🎯 PRIORITY TARGETS")
    if path.exists():
        print(path.read_text())
    else:
        print("No priority targets found.")

def show_summary(base_dir):
    path = base_dir / "attack_surface" / "attack_surface_summary.txt"
    header("📋 ATTACK SURFACE SUMMARY")
    if path.exists():
        print(path.read_text())
    else:
        print("No summary available.")

def show_semantic(base_dir):
    path = base_dir / "semantic_results.json"
    header("🧠 HIGH IMPACT SEMANTIC TARGETS")
    data = load_json(path)
    if not data:
        print("No semantic data.")
        return

    for entry in data:
        #impact = entry.get("impact", 0)
        impact = entry.get("impact_score", 0)

        if impact >= 70:
            print(f"[{impact}] {entry.get('subdomain')}  → {entry.get('tags')}")

def show_probe(base_dir):
    web = base_dir / "probe" / "web_hosts.txt"
    header("🌐 LIVE WEB HOSTS")
    if web.exists():
        lines = web.read_text().splitlines()
        for l in lines[:20]:
            print(l)
        if len(lines) > 20:
            print(f"... ({len(lines)} total)")
    else:
        print("No probe data.")

def show_diff(base_dir):
    path = base_dir / "scan_diff.json"
    header("🕒 TEMPORAL CHANGES")
    data = load_json(path)
    if not data:
        print("No diff data.")
        return

    for k in ("new", "escalated", "disappeared"):
        if k in data and data[k]:
            print(f"\n{k.upper()}:")
            for item in data[k]:
                print(f"  - {item}")

def main():
    if len(sys.argv) != 2:
        print("Usage: tugarecon_view.py <results/target/date>")
        sys.exit(1)

    base_dir = Path(sys.argv[1])
    if not base_dir.exists():
        print("Invalid path.")
        sys.exit(1)

    print("\n🧭 TugaRecon – Quick View\n")
    show_priority_targets(base_dir)
    show_summary(base_dir)
    show_semantic(base_dir)
    show_probe(base_dir)
    show_diff(base_dir)

if __name__ == "__main__":
    main()
