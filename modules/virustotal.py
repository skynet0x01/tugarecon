# TugaRecon - virustotal, write by LordNeoStark
# import modules
import time
import requests

from functions import useragent
from functions import write_file
from functions import G,W

class Virustotal:

    def __init__(self, target, output):

        subdomains = set()
        count = 0
        subdomainscount = 0
        start_time = time.time()
        self.module_name = "VirusTotal"
        self.engine = "virustotal"

        print(G + f"VirusTotal: Enumerating subdomains now for {target} \n" + W)

        url = f'https://www.virustotal.com/ui/domains/{target}/subdomains?limit=40'

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})

            while subdomainscount < 40:
                subdomains = response.json()["data"][subdomainscount]["id"]
                subdomainscount = subdomainscount + 1
                count = count + 1
                print(f"[*] {subdomains}")

                if output is not None:
                    write_file(subdomains, self.engine +output)

            if output:
                print(f"\nSaving result... {self.engine +output}")

            print(G + f"\n[**] TugaRecon is complete. VirusTotal: {count} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

            if not subdomains:
                print(f"[x] No data found for {target} using VirusTotal.")

        except ValueError:
            pass