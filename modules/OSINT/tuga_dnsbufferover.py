# --------------------------------------------------------------------------------------------------
# TugaRecon – DNSBufferOver Module
# Author: Skynet0x01 2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import time
import requests
import urllib3

from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Import internal functions
from utils.tuga_save import write_file

# ----------------------------------------------------------------------------------------------------------
class DNSBufferOver:

    def __init__(self, target):
        """
        Constructor: recebe o domínio alvo (target).
        Executa engine_url() que devolve JSON (ou None em caso de erro)
        e chama enumerate() se a resposta for válida.
        """
        self.target = target
        self.module_name = "DNSBufferOver"
        self.engine = "dnsbufferover"
        self.response = self.engine_url()

        if self.response:
            self.enumerate(self.response, target)
        else:
            pass

# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        """
        Faz GET ao endpoint público do DNSBufferOver.
        Retorna JSON com subdomínios históricos ou None em caso de erro.
        """
        url = f"https://dns.bufferover.run/dns?q=.{self.target}"
        try:
            r = requests.get(url, timeout=20, verify=False)
            r.raise_for_status()
            return r.json()
        except (requests.ConnectionError, requests.Timeout, requests.RequestException):
            return None

# ----------------------------------------------------------------------------------------------------------
    def enumerate(self, data, target):
        """
        Extrai subdomínios do JSON retornado.
        Utiliza write_file para armazenar subdomínios.
        """
        subdomains_found = set()
        self.subdomainscount = 0
        start_time = time.time()

        try:
            fdns = data.get("FDNS_A", [])
            rdns = data.get("RDNS", [])

            # FDNS_A -> formato: sub.example.com,IP
            for entry in fdns:
                sub = entry.split(",")[0].strip()
                if sub and sub not in subdomains_found:
                    subdomains_found.add(sub)
                    self.subdomainscount += 1
                    write_file(sub, target)

            # RDNS -> formato: IP,sub.example.com
            for entry in rdns:
                sub = entry.split(",")[1].strip()
                if sub and sub not in subdomains_found:
                    subdomains_found.add(sub)
                    self.subdomainscount += 1
                    write_file(sub, target)

        except Exception:
            pass

        elapsed = time.time() - start_time
        self.elapsed = elapsed
        self.subdomains = sorted(subdomains_found)

# ----------------------------------------------------------------------------------------------------------
