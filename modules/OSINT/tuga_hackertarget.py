# --------------------------------------------------------------------------------------------------
# TugaRecon – HackerTarget OSINT Module
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
class Hackertarget:
    def __init__(self, target):
        self.target = target
        self.module_name = "HackerTarget"
        self.engine = "hackertarget"
        self.subdomains = set()
        self.subdomainscount = 0

        response = self.engine_url()
        if response:
            self.enumerate(response)

    # --------------------------------------------------------------------------------------------------
    def engine_url(self):
        url = f"https://api.hackertarget.com/hostsearch/?q={self.target}"
        headers = {
            "User-Agent": "TugaRecon/2.x (+https://github.com/skynet0x01/tugarecon)"
        }

        try:
            r = requests.get(url, headers=headers, timeout=15, verify=False)
            if r.status_code != 200:
                log.debug(f"[HackerTarget] HTTP {r.status_code} for {self.target}")
                return None

            text = r.text.strip()
            if not text or "API count exceeded" in text or "error" in text.lower():
                #log.info("[HackerTarget] API limit reached or empty response")
                return None

            return text

        except (requests.ConnectionError, requests.Timeout) as e:
            log.debug(f"[HackerTarget] Request failed: {e}")
            return None

    # --------------------------------------------------------------------------------------------------
    def enumerate(self, response_text):
        start_time = time.time()

        try:
            lines = response_text.splitlines()

            for line in lines:
                line = line.strip()
                if not line or "," not in line:
                    continue

                host = line.split(",")[0].strip().lower()
                if not host or host in self.subdomains:
                    continue

                self.subdomains.add(host)
                self.subdomainscount += 1
                write_file(host, self.target)

            elapsed = round(time.time() - start_time, 2)
            #log.info(f"[HackerTarget] {self.subdomainscount} unique subdomains found in {elapsed}s")

        except Exception as e:
            log.debug(f"[HackerTarget] Parsing error: {e}")




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
# class Hackertarget:
#
#     def __init__(self, target):
#
#         self.target = target
#         self.module_name = "HackerTarget"
#         self.engine = "hackertarget"
#         self.response = self.engine_url()
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
#             response = requests.get(f"https://api.hackertarget.com/hostsearch/?q={self.target}").text
#             return response
#         except requests.ConnectionError:
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
#             extract_sub = response.split("\n")
#             #print(extract_sub)
#             for i in extract_sub:
#                 if "API count exceeded " in i:
#                     pass
#                 else:
#                     filters = i.split(",")
#                     subdomains = filters[0]
#                     #print(f"    [*] {subdomains}")
#                     write_file(subdomains, target)
#         except Exception as e:
#             pass
# # ----------------------------------------------------------------------------------------------------------

