# import modules
import time
import requests

from functions import useragent
from functions import write_file


class Certspotter:

    def __init__(self, target, output):

        subdomains = set()
        count = 0
        subdomainscount = 0
        start_time = time.time()
        self.module_name = "CertSpotter"
        self.engine = "certspotter"

        print(f"\nCertSpotter: Enumerating subdomains now for {target} \n")

        url = f'https://api.certspotter.com/v1/issuances?domain={target}&include_subdomains=true&expand=dns_names'

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})

            while subdomainscount < 100:
                subdomains = response.json()[subdomainscount]["dns_names"][0]
                subdomainscount = subdomainscount + 1
                count = count + 1
                print(f"[*] {subdomains}")

                if output is not None:
                    write_file(subdomains, self.engine +output)

            if output:
                print(f"\nSaving result... {self.engine +output}")

            print(f"\n[**] TugaRecon is complete. CertSpotter: {count} subdomains have been found in %s seconds" % (
                    time.time() - start_time))

            if not subdomains:
                print(f"[x] No data found for {target} using CertSpotter.")

        except ValueError:
            pass
