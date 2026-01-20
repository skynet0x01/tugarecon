# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import time
from utils.tuga_colors import G, R, W


# ----------------------------------------------------------------------------------------------------------
# Run all Modules...
def queries(target):
    print("")
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(G + "Enumerating subdomains for " + target + " ...\n" + W)
    time.sleep(1)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print(R + "[-] Searching " + target + " in CertsPotter " + W)
    print(R + "[-] Searching " + target + " in SSL Certificates " + W)
    print(R + "[-] Searching " + target + " in HackerTarget " + W)
    print(R + "[-] Searching " + target + " in ThreatCrowd " + W)
    print(R + "[-] Searching " + target + " in Alienvault " + W)
    print(R + "[-] Searching " + target + " in Threatminer" + W)
    print(R + "[-] Searching " + target + " in Omnisint" + W)
    print(R + "[-] Searching " + target + " in DNSDumpster" + W)
    print(R + "[-] Searching " + target + " in API Sublist3r" + W)
    print(R + "[-] Searching " + target + " in DNSBufferOver" + W)
    print(R + "[-] Searching " + target + " in RapidDNS\n" + W)
    print(G + "────────────────────────────────────────────────────────────" + W)
    print("")
    print(G + "[IA] Intelligence‑Assisted Wordlist Enrichment\n" + W)
    #time.sleep(0.5)
    return (0)
