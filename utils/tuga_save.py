# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import os
import time
import datetime

from utils.tuga_colors import G, Y, R, W
from utils.tuga_functions import print_semantic_results, print_semantic_results_grouped
from modules.IA.semantic import classify
from modules.IA.impact_score import compute_impact_score
from modules.IA.scan_diff_view import print_scan_diff
from utils.tuga_exporters import export_json, export_priority_lists
from utils.tuga_scan_diff import diff_scans, export_diff, get_previous_scan_date


# ----------------------------------------------------------------------------------------------------------
def write_high_value_targets(results, target):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()

    high_value = [
        r for r in results
        if r.get("impact_score", 0) >= 40
           or r.get("priority") in ("CRITICAL", "HIGH")
    ]

    if not high_value:
        return

    folder = os.path.join(pwd, "results/" + target + "/" + date + "/" + "high_value_targets.txt")

    #output_file = "results/" + target + "/" + date + "/" + "high_value_targets.txt"

    with open(folder, "w") as f:
        for r in high_value:
            f.write(
                f"{r['subdomain']:<50} "
                f"[{r['priority']:<8}] "
                f"score={r['impact_score']:>3} "
                f"tags={','.join(r['tags'])}\n"
            )


# ----------------------------------------------------------------------------------------------------------
def write_file_bruteforce(subdomains, target):  # 26/05/2025
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()
    # saving subdomains results to output file
    folder = os.path.join(pwd, "results/" + target + "/" + date)
    try:
        os.makedirs(folder)
    except:
        pass
    try:
        with open("results/" + target + "/" + "bruteforce.txt", 'a') as tmp:
            tmp.write(subdomains + '\n')
        tmp.close()
    except:
        pass


# ----------------------------------------------------------------------------------------------------------
def BruteForceReadFile(target, start_time):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()
    folder = os.path.join(pwd, "results/" + target + "/" + date)
    file = open("results/" + target + "/" + date + "/" + "tuga_bruteforce.txt", 'r')
    lines = file.readlines()

    for index, line in enumerate(lines):
        print("     [*] {}:  {}".format(index, line.strip()))
    file.close()
    print(Y + "\n[*] Total Subdomains Found: {}".format(index) + W)
    print(Y + f"[**]TugaRecon: Subdomains have been found in %s seconds" % (time.time() - start_time) + "\n" + W)
    print(Y + "\n[+] Output Result" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W, folder + "\n")


# ----------------------------------------------------------------------------------------------------------
def write_file(subdomains, target):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()

    # saving subdomains results to output file
    folder = os.path.join(pwd, "results/" + target + "/" + date)
    try:
        os.makedirs(folder)
    except:
        pass
    try:
        with open("results/" + target + "/" + "tmp.txt", 'a') as tmp:
            tmp.write(subdomains + '\n')
        tmp.close()
    except:
        pass


# ----------------------------------------------------------------------------------------------------------
def DeleteDuplicate(target):
    date = str(datetime.datetime.now().date())
    content = open("results/" + target + "/" + "tmp.txt", 'r').readlines()
    content_set = set(content)
    cleandata = open("results/" + target + "/" + date + "/" + "osint_subdomains.txt", 'w')
    for line in content_set:
        cleandata.write(line)
    try:
        os.remove("results/" + target + "/" + "tmp.txt")
    except OSError:
        pass


# ----------------------------------------------------------------------------------------------------------
def ReadFile(target, start_time):
    # Define paths
    date = str(datetime.datetime.now().date())
    folder = os.path.join("results", target, date)
    os.makedirs(folder, exist_ok=True)

    subdomains_path = os.path.join(folder, "osint_subdomains.txt")
    if not os.path.exists(subdomains_path):
        print(R + f"[!] No subdomains file found for {target} on {date}" + W)
        return

    # Read subdomains
    with open(subdomains_path, "r") as file:
        lines = file.readlines()

    # Classify and compute impact scores
    classified = []
    results = []

    for s in lines:
        semantic = classify(s.strip())
        scored = compute_impact_score(semantic)
        classified.append(scored)
        results.append(scored)

    # Print semantic results
    #print_semantic_results(classified)
    print_semantic_results_grouped(classified)

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
        print(G + f"[Δ] Diff generated against {prev_date}" + W)
    else:
        print(Y + "[Δ] No previous scan found (baseline created)" + W)

    # Summary
    elapsed = time.time() - start_time
    print(Y + f"[**] TugaRecon: Scan completed in {elapsed:.2f} seconds\n" + W)
    print(Y + "[+] Output directory" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W + folder + "\n")
# ----------------------------------------------------------------------------------------------------------
