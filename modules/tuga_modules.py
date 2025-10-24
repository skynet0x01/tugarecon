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
from modules import tuga_dnsdumpster
from utils.tuga_colors import G, R, W


# ----------------------------------------------------------------------------------------------------------
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
    print(R + "[-] Searching " + target + " in DNSDumpster" + W)
    print(R + "[-] Searching " + target + " in API Sublist3r\n" + W)
    #time.sleep(0.5)
    return (0)
