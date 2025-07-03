#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# ----------------------------------------------------------------------------------------------------------
import os
from utils.tuga_colors import G, Y, B, R, W

# ----------------------------------------------------------------------------------------------------------
def main_work_subdirs():
    rootdir = "results"
    print("\nResults: ")
    print(G + "**************************************************************" + W)
    for root, dirs, files in os.walk(rootdir):
        dirs.sort()
        if root == rootdir:
            for domain in dirs:
                print(Y + f"[Domain]", domain  + W)
