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

import urllib.request
import webbrowser
import urllib.error
import os
import time
import datetime
from pathlib import Path # Future: Nedd to change to pathlib2

from utils.tuga_colors import G, Y, R, W
from modules.ia_subdomain.semantic import classify

# ----------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
def print_semantic_results(classified):
    """
    Pretty-print semantic classification results with colorized risk.
    """

    RISK_ORDER = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1
    }

    RISK_COLOR = {
        "HIGH": R,
        "MEDIUM": Y,
        "LOW": G
    }

    classified = sorted(
        classified,
        key=lambda x: RISK_ORDER.get(x["risk_hint"], 0),
        reverse=True
    )

    print("\n[🧠] Semantic Classification Results\n")

    for idx, item in enumerate(classified, 1):
        risk = item["risk_hint"]
        color = RISK_COLOR.get(risk, W)

        tags = ", ".join(item["tags"]) if item["tags"] else "-"

        print(
            f"[{idx:04d}] "
            f"[{color}{risk:^6}{W}] "
            f"{item['subdomain']:<60} "
            f"tags: {tags:<25} "
            f"→ {item['reason']}"
        )


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
    file = open("results/" + target + "/" + date + "/" + "subdomains.txt", 'r')

    lines = file.readlines()

    classified = [classify(s) for s in lines]
    print_semantic_results(classified)

    print(Y + f"[**]TugaRecon: Subdomains have been found in %s seconds" % (time.time() - start_time) +"\n"+ W)
    print(Y + "\n[+] Output Result" + W)
    print(G + "**************************************************************" + W)
    print(R + "         ->->-> " + W, folder + "\n")


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
    print(Y + f"[**]TugaRecon: Subdomains have been found in %s seconds" % (time.time() - start_time) +"\n"+ W)
    print(Y + "\n[+] Output Result" + W)
    print(G + "**************************************************************" + W)
    print(R + "         ->->-> " + W, folder + "\n")
    
    
# ----------------------------------------------------------------------------------------------------------
def mapping_domain(target):
    date = str(datetime.datetime.now().date())
    if not os.path.exists("results/" + target + "/" + date):
        os.mkdir("results/" + target + "/" + date)
    else:
        pass
    try:
        try:
            urllib.request.urlretrieve(f"https://dnsdumpster.com/static/map/{target}" + ".png",
                                       f"results/{target}/"+ date + f"/{target}.png")
        except urllib.error.URLError as e:
            print("", e.reason)
        my_file = Path(f"results/{target}/"+ date + f"/{target}.png")
        if my_file.is_file():
            webbrowser.open(f"results/{target}/"+ date + f"/{target}.png")
        else:
            print(Y + "\nOops! The map file was not generated. Try again...\n" + W)
    except PermissionError:
        print("You dont have permission to save a file, use sudo su")
