## TugaRecon - crt module, write by LordNeoStark
# import modules

import time
import requests
import re

from functions import useragent
from functions import write_file
from functions import G, W

class CRT:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.count = 0
        self.module_name = "SSL Certificates"
        self.engine = "crt"

        print(G + f"SSL Certificates: Enumerating subdomains now for {target} \n" + W)

        url = self.subdomains_list()
        self.enumerate(url, output)

    def subdomains_list(self):
        # target = target.replace("*", "%25")
        url = f"https://crt.sh/?q={self.target}&output=json"
        return url

    def enumerate(self, url, output):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})
            regex = r'[^%*].*'
            data = response.json()

            if data:
                for row in data:
                    row = re.findall(regex, row["name_value"])[0]
                    subdomains.add(row)

                # print("\n[*] ".join(subdomains))

                subs = sorted(set(subdomains))

                for s in subs:
                    if "@" not in s:  # filter for emails
                        self.count = self.count + 1
                        print(f"[*] {s}")
                        if output is not None:
                            write_file(s, self.engine + output)

                if output:
                    print(f"\nSaving result... {self.engine + output}")

        except IndexError:
            pass

        print(G + f"\n[**] TugaRecon is complete. SSL Certificates: {self.count} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {self.target} using SSL Certificates.")