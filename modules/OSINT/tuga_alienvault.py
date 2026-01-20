# --------------------------------------------------------------------------------------------------
# TugaRecon – AlienVault OSINT Module
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import time
import requests
import json
import logging

from utils.tuga_save import write_file

log = logging.getLogger("tugarecon")

# --------------------------------------------------------------------------------------------------
class Alienvault:
    def __init__(self, target):
        self.target = target
        self.module_name = "Alienvault"
        self.engine = "alienvault"
        self.subdomains = set()
        self.subdomainscount = 0

        response = self.engine_url()
        if response:
            self.enumerate(response)

    # --------------------------------------------------------------------------------------------------
    def engine_url(self):
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{self.target}/passive_dns"
        headers = {
            "User-Agent": "TugaRecon/2.x (+https://github.com/skynet0x01/tugarecon)"
        }

        try:
            r = requests.get(url, headers=headers, timeout=15, verify=False)
            if r.status_code != 200:
                log.debug(f"[Alienvault] HTTP {r.status_code} for {self.target}")
                return None
            return r.text
        except requests.RequestException as e:
            log.debug(f"[Alienvault] Request failed: {e}")
            return None

    # --------------------------------------------------------------------------------------------------
    def enumerate(self, response_text):
        start_time = time.time()

        try:
            data = json.loads(response_text)
            for item in data.get("passive_dns", []):
                host = item.get("hostname")
                if host:
                    host = host.strip().lower()
                    if host not in self.subdomains:
                        self.subdomains.add(host)
                        self.subdomainscount += 1
                        write_file(host, self.target)

            elapsed = round(time.time() - start_time, 2)
            #log.info(f"[Alienvault] {self.subdomainscount} subdomains found in {elapsed}s")

        except Exception as e:
            log.debug(f"[Alienvault] Parsing error: {e}")


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
# import json
#
# from requests.packages.urllib3.exceptions import InsecureRequestWarning
#
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#
# from utils.tuga_save import write_file
#
#
# # ----------------------------------------------------------------------------------------------------------
# class Alienvault:
#     def __init__(self, target):
#         self.target = target
#         self.module_name = "Alienvault"
#         self.engine = "alienvault"
#         self.response = self.engine_url()  # URL
#
#         if self.response != 1:
#             self.enumerate(self.response, target)  # Call the function enumerate
#         else:
#             pass
#
#     # ----------------------------------------------------------------------------------------------------------
#     def engine_url(self):
#         try:
#             response = requests.get(
#                 f'https://otx.alienvault.com/api/v1/indicators/domain/{self.target}/passive_dns').text
#             return response
#         except requests.ConnectionError:
#             response = 1
#             return response
#
#     # ----------------------------------------------------------------------------------------------------------
#     def enumerate(self, response, target):
#         subdomains = []
#         self.subdomainscount = 0
#         start_time = time.time()
#         #################################
#         try:
#             extract_sub = json.loads(response)
#             #print(extract_sub)
#             for i in extract_sub['passive_dns']:
#                 subdomains = i['hostname']
#                 self.subdomainscount = self.subdomainscount + 1
#                 #print(f"    [*] {subdomains}")
#                 write_file(subdomains, target)
#         except Exception as e:
#             pass
# # ----------------------------------------------------------------------------------------------------------
#
