#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2025

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2025 skynet0x01
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.

# import go here
# ----------------------------------------------------------------------------------------------------------
import os
import time
import datetime

from utils.tuga_colors import G, Y, R, W
from utils.tuga_functions import print_semantic_results
from modules.ia_subdomain.semantic import classify
from modules.ia_subdomain.impact_score import compute_impact_score

# ----------------------------------------------------------------------------------------------------------
def write_high_value_targets(results, target):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()

    high_value = [
        r for r in results
        if r.get("impact_score", 0) >= 35
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
def write_file_bruteforce(subdomains, target): # 26/05/2025
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
    cleandata = open("results/" + target + "/" + date + "/" + "subdomains.txt", 'w')
    for line in content_set:
        cleandata.write(line)
    try:
        os.remove("results/"+ target + "/" + "tmp.txt")
    except OSError:
        pass


# ----------------------------------------------------------------------------------------------------------
def ReadFile(target, start_time):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()
    folder = os.path.join(pwd, "results/" + target + "/" + date)
    os.makedirs(folder, exist_ok=True)

    file = open("results/" + target + "/" + date + "/" + "subdomains.txt", 'r')

    lines = file.readlines()

    #classified = [classify(s) for s in lines]
    classified = []
    results = []

    for s in lines:
        semantic = classify(s.strip())
        scored = compute_impact_score(semantic)
        classified.append(scored)
        results.append(scored)

    print_semantic_results(classified)
    write_high_value_targets(results, target)

    print(Y + f"[**]TugaRecon: Subdomains have been found in %s seconds" % (time.time() - start_time) +"\n"+ W)
    print(Y + "\n[+] Output Result" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "         ->->-> " + W, folder + "\n")

    #write_high_value_targets(results, target)


# ----------------------------------------------------------------------------------------------------------