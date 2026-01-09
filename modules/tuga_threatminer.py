#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2026

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2026.
#
# Copyright (C) 2026 skynet0x01
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
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import internal functions
from utils.tuga_save import write_file


# ----------------------------------------------------------------------------------------------------------
class Threatminer:
    def __init__(self, target):
        self.target = target
        self.module_name = "Threatminer"
        self.engine = "threatminer"
        self.response = self.engine_url() # URL

        if self.response != 1:
            self.enumerate(self.response, target) # Call the function enumerate
        else:
            pass
        
        
# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        try:
            response = requests.get(f'https://api.threatminer.org/v2/domain.php?q={self.target}&rt=5').text
            return response
        except requests.ConnectionError:
            response = 1
            return response
        
        
# ----------------------------------------------------------------------------------------------------------
    def enumerate(self, response, target):
        subdomains = []
        self.subdomainscount = 0
        start_time = time.time()
        #################################
        try:
            extract_sub = json.loads(response)
            #print(extract_sub)
            for i in extract_sub['results']:
                subdomains = i
                self.subdomainscount = self.subdomainscount + 1
                #print(f"    [*] {subdomains}")
                write_file(subdomains, target)
        except Exception as e:
            pass
# ----------------------------------------------------------------------------------------------------------

