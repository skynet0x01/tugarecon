# TugaRecon - threatcrowd, write by LordNeoStark
# import modules
import time
import requests

from functions import useragent
from functions import write_file
from functions import G,W

class Threatcrowd:

    def __init__(self, target, output):

        subdomains = set()
        count = 0
        subdomainscount = 0
        start_time = time.time()
        self.module_name = "Threat Crowd"
        self.engine = "certspotter"

        print(G + f"Threat Crowd: Enumerating subdomains now for {target} \n" + W)

        url = f'https://threatcrowd.org/searchApi/v2/domain/report/?domain={target}'

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})

            while subdomainscount < 500:
                subdomains = response.json()["subdomains"][subdomainscount]
                subdomainscount = subdomainscount + 1
                count = count + 1
                print(f"[*] {subdomains}")

                if output is not None:
                    write_file(subdomains, self.engine +output)

            if output:
                print(f"\nSaving result... {self.engine +output}")

            print(G + f"\n[**] TugaRecon is complete. Threat Crowd: {count} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

            if not subdomains:
                print(f"[x] No data found for {target} using Threat Crowd.")

        except ValueError:
            pass
