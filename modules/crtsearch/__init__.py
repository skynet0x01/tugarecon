# import modules
import re
import time
import requests

from tugarecon import useragent
from tugarecon import write_file


class CRTsearch:

    def __init__(self, target, output):

        subdomains = set()
        count = 0
        start_time = time.time()
        self.module_name = "SSL Certificates"

        print(f"Enumerating subdomains now for {target} \n")

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
                            write_file(s, output)

                if output:
                    print(f"\nSaving result... {output}")

                print(f"\n[**] TugaRecon is complete, {count} subdomains have been found in %s seconds" % (time.time() - start_time))

            elif not data:
                print(f"[x] No data found for {target} using crtsh.")

        except ValueError:
            pass
