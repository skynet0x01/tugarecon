# --------------------------------------------------------------------------------------------------
# TugaRecon – Omnisint OSINT Module
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import time
import requests
import logging
import urllib3

from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

from utils.tuga_save import write_file

log = logging.getLogger("tugarecon")

# --------------------------------------------------------------------------------------------------
class Omnisint:
    def __init__(self, target):
        self.target = target
        self.module_name = "Omnisint"
        self.engine = "omnisint"
        self.subdomains = set()
        self.subdomainscount = 0

        response = self.engine_url()
        if response:
            self.enumerate(response)

    # --------------------------------------------------------------------------------------------------
    def engine_url(self):
        url = f"https://sonar.omnisint.io/subdomains/{self.target}"
        headers = {
            "User-Agent": "TugaRecon/2.x (+https://github.com/skynet0x01/tugarecon)"
        }
        try:
            r = requests.get(url, headers=headers, timeout=15, verify=False)
            if r.status_code != 200:
                log.debug(f"[Omnisint] HTTP {r.status_code} for {self.target}")
                return None
            return r.json()
        except (requests.ConnectionError, requests.Timeout, requests.JSONDecodeError) as e:
            log.debug(f"[Omnisint] Request failed: {e}")
            return None

    # --------------------------------------------------------------------------------------------------
    def enumerate(self, response_json):
        start_time = time.time()
        try:
            for host in response_json:
                host = host.strip().lower()
                if not host or host in self.subdomains:
                    continue
                self.subdomains.add(host)
                self.subdomainscount += 1
                write_file(host, self.target)

            elapsed = round(time.time() - start_time, 2)
            #log.info(f"[Omnisint] {self.subdomainscount} unique subdomains found in {elapsed}s")

        except Exception as e:
            log.debug(f"[Omnisint] Parsing error: {e}")



# # --------------------------------------------------------------------------------------------------
# # TugaRecon
# # Author: Skynet0x01 2020-2026
# # GitHub: https://github.com/skynet0x01/tugarecon
# # License: GNU GPLv3
# # Patent Restriction Notice:
# # No patents may be claimed or enforced on this software or any derivative.
# # Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# # --------------------------------------------------------------------------------------------------
# import time
# import requests
# import urllib3
#
# from urllib3.exceptions import InsecureRequestWarning
# urllib3.disable_warnings(InsecureRequestWarning)
#
# # Import internal functions
# from utils.tuga_save import write_file
#
#
# # ----------------------------------------------------------------------------------------------------------
# class Omnisint:
#     def __init__(self, target):
#         self.target = target
#         self.module_name = "Omnisint"
#         self.engine = "omnisint"
#         self.response = self.engine_url() # URL
#
#         if self.response != 1:
#             self.enumerate(self.response, target) # Call the function enumerate
#         else:
#             pass
#
#
# # ----------------------------------------------------------------------------------------------------------
#     def engine_url(self):
#         try:
#             response = requests.get(f"https://sonar.omnisint.io/subdomains/{self.target}").json()
#             return response
#         except (requests.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.JSONDecodeError):
#             response = 1
#             return response
#
#
# # ----------------------------------------------------------------------------------------------------------
#     def enumerate(self, response, target):
#         subdomains = []
#         self.subdomainscount = 0
#         start_time = time.time()
#         #################################
#         try:
#             extract_sub = response
#             for i in extract_sub:
#                 subdomains = i
#                 self.subdomainscount = self.subdomainscount + 1
#                 #print(f"    [*] {subdomains}")
#                 write_file(subdomains, target)
#         except Exception as e:
#             pass
# # ----------------------------------------------------------------------------------------------------------
#
