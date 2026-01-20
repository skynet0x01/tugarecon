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
import requests
import re
import urllib3

from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Import internal functions
from utils.tuga_save import write_file


# ----------------------------------------------------------------------------------------------------------
class RapidDNS:

    def __init__(self, target):
        self.target = target
        self.module_name = "RapidDNS"
        self.engine = "rapiddns"
        self.response = self.engine_url()

        if self.response != 1:
            self.enumerate(self.response, target)
        else:
            pass


# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        """
        Scrape rapiddns.io for subdomains related to the target domain.
        """
        try:
            url = f"https://rapiddns.io/subdomain/{self.target}?full=1"
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            return response.text
        except requests.RequestException:
            return 1


# ----------------------------------------------------------------------------------------------------------
    def enumerate(self, response, target):
        subdomains_found = set()
        self.subdomainscount = 0
        start_time = time.time()

        try:
            # Regex simples para apanhar subdomínios do target dentro do HTML
            pattern = re.compile(r'([A-Za-z0-9_\-\.]+\.%s)' % re.escape(target), re.IGNORECASE)
            matches = pattern.findall(response)

            for match in matches:
                sub = match.strip().strip('.,;:"\'()[]{}<>')
                if sub and sub not in subdomains_found:
                    subdomains_found.add(sub)
                    self.subdomainscount += 1
                    try:
                        write_file(sub, target)
                    except Exception:
                        pass

        except Exception:
            pass

        elapsed = time.time() - start_time
        self.elapsed = elapsed
        self.subdomains = sorted(subdomains_found)

# ----------------------------------------------------------------------------------------------------------
