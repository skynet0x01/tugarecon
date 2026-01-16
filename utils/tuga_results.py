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
from utils.tuga_colors import G, Y, B, R, W

# ----------------------------------------------------------------------------------------------------------
def main_work_subdirs():
    rootdir = "results"
    print("\nResults: ")
    print(G + "────────────────────────────────────────────────────────────" + W)
    for root, dirs, files in os.walk(rootdir):
        dirs.sort()
        if root == rootdir:
            for domain in dirs:
                print(Y + f"[Domain]", domain  + W)
