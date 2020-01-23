## TugaRecon - crt module, write by LordNeoStark
# import modules
import re
import time
import requests

from functions import useragent
from functions import write_file
from functions import G,W
class CRT:

    def __init__(self, target, output):

        subdomains = set()
        count = 0
        start_time = time.time()
        self.module_name = "SSL Certificates"
        self.engine = "crt"

        print(G + f"CRT: Enumerating subdomains now for {target} \n" + W)

        # target = target.replace("*", "%25")
        url = f"https://crt.sh/?q={target}&output=json"

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
                        count = count + 1
                        print(f"[*] {s}")
                        if output is not None:
                            write_file(s, self.engine +output)

                if output:
                    print(f"\nSaving result... {self.engine +output}")

                print(f"\n[**] TugaRecon is complete. CRT: {count} subdomains have been found in %s seconds" % (
                        time.time() - start_time))

            elif not data:
                print(f"[x] No data found for {target} using crtsh.")

        except ValueError:
            pass
