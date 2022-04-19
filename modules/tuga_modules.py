# TugaRecon - module, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# import modules
import time
# Import internal modules
from modules import tuga_certspotter
from modules import tuga_crt
from modules import tuga_hackertarget
from modules import tuga_threatcrowd
from modules import tuga_alienvault
from modules import tuga_threatminer
from modules import tuga_omnisint
from modules import tuga_sublist3r
from utils.tuga_colors import G, Y, B, R, W
################################################################################
# Run all Modules...
def queries(target):
    print(G + "Enumerating subdomains for " + target + " ...\n" + W)
    time.sleep(1)
    print(R + "[-] Searching " + target + " in CertsPotter " + W)
    print(R + "[-] Searching " + target + " in SSL Certificates " + W)
    print(R + "[-] Searching " + target + " in HackerTarget " + W)
    print(R + "[-] Searching " + target + " in ThreatCrowd " + W)
    print(R + "[-] Searching " + target + " in Alienvault " + W)
    print(R + "[-] Searching " + target + " in Threatminer" + W)
    print(R + "[-] Searching " + target + " in Omnisint" + W)
    print(R + "[-] Searching " + target + " in API Sublist3r\n" + W)
    #time.sleep(0.5)
    return (0)
