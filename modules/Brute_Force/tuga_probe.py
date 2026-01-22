# --------------------------------------------------------------------------------------------------
# TugaRecon – Service Probe Module (Refactored, Compact Output)
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import asyncio
import httpx
import os
import json
import time
import logging

from utils.tuga_colors import G, Y, R, W

logging.getLogger("httpx").disabled = True

class TugaServiceProbe:

    def __init__(self, input_file, output_dir, concurrency=50, timeout=6, retries=2, verbose=False):
        self.input_file = input_file
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.timeout = timeout
        self.retries = retries
        self.verbose = verbose

        self.web_hosts = []
        self.dead_hosts = []
        self.services = []

        os.makedirs(self.output_dir, exist_ok=True)

    # --------------------------------------------------------------------------------------------------
    def load_hosts(self):
        hosts = []
        with open(self.input_file) as f:
            for line in f:
                h = line.strip().split("\t")[0]
                if h:
                    hosts.append(h)
        return hosts

    # --------------------------------------------------------------------------------------------------
    async def probe_host(self, client, host):
        """Tenta HTTPS e depois HTTP, com retries."""
        for attempt in range(1, self.retries + 2):
            for scheme in ["https", "http"]:
                url = f"{scheme}://{host}"
                try:
                    r = await client.get(url, follow_redirects=True)
                    service = {
                        "host": host,
                        "url": str(r.url),
                        "status": r.status_code,
                        "title": self.extract_title(r.text),
                        "server": r.headers.get("server", ""),
                        "scheme": scheme,
                        "redirected": str(r.url) != url
                    }
                    return service
                except httpx.RequestError:
                    continue
            await asyncio.sleep(0.05)
        return None

    # --------------------------------------------------------------------------------------------------
    def extract_title(self, html):
        if not html:
            return ""
        html_lower = html.lower()
        start = html_lower.find("<title>")
        end = html_lower.find("</title>")
        if start != -1 and end != -1:
            return html[start+7:end].strip()
        return ""

    # --------------------------------------------------------------------------------------------------
    async def run_async(self, hosts):
        limits = httpx.Limits(max_connections=self.concurrency)
        timeout = httpx.Timeout(self.timeout)

        async with httpx.AsyncClient(limits=limits, timeout=timeout, verify=False) as client:
            sem = asyncio.Semaphore(self.concurrency)

            async def bound_probe(host):
                async with sem:
                    try:
                        result = await self.probe_host(client, host)
                        return host, result
                    except Exception:
                        return host, None

            tasks = [bound_probe(h) for h in hosts]

            total = len(hosts)
            completed = 0

            for coro in asyncio.as_completed(tasks):
                host, result = await coro
                completed += 1

                if result:
                    self.services.append(result)
                    self.web_hosts.append(host)
                    if self.verbose:
                        # print(G + f"[+] {host} → {result['status']} {result['scheme']} {result['title']}" + W)
                        pass
                else:
                    self.dead_hosts.append(host)
                    if self.verbose:
                        # print(R + f"[-] {host} dead" + W)
                        pass

                # Print progress every 10 hosts or at the end
                if completed % 10 == 0 or completed == total:
                    print(Y + f"[*] Probing hosts... {completed}/{total}" + W, end="\r")

    # --------------------------------------------------------------------------------------------------
    def save_results(self):
        services_path = os.path.join(self.output_dir, "services.json")
        webhosts_path = os.path.join(self.output_dir, "web_hosts.txt")
        deadhosts_path = os.path.join(self.output_dir, "dead_hosts.txt")

        with open(services_path, "w") as f:
            json.dump(self.services, f, indent=2)

        with open(webhosts_path, "w") as f:
            for h in sorted(set(self.web_hosts)):
                f.write(h + "\n")

        with open(deadhosts_path, "w") as f:
            for h in sorted(set(self.dead_hosts)):
                f.write(h + "\n")

        print(G + f"[+] Saved {len(self.services)} services" + W)

    # --------------------------------------------------------------------------------------------------
    def run(self):
        print(Y + "[*] Loading hosts..." + W)
        hosts = self.load_hosts()
        print(Y + f"[*] Probing {len(hosts)} hosts..." + W)

        start = time.time()

        try:
            asyncio.run(self.run_async(hosts))
        except Exception as e:
            print(R + f"[!] Probe crashed: {e}" + W)

        self.save_results()

        print(G + f"\n[+] Probe completed in {time.time() - start:.2f}s" + W)
        print(G + f"[+] Alive hosts: {len(self.web_hosts)} | Dead hosts: {len(self.dead_hosts)}" + W)
        print(G + f"[+] Results saved in: {self.output_dir}" + W)


# # --------------------------------------------------------------------------------------------------
# # TugaRecon – Service Probe Module (Refactored)
# # Author: Skynet0x01 2020-2026
# # GitHub: https://github.com/skynet0x01/tugarecon
# # License: GNU GPLv3
# # Patent Restriction Notice:
# # No patents may be claimed or enforced on this software or any derivative.
# # Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# # --------------------------------------------------------------------------------------------------
#
# import asyncio
# import httpx
# import os
# import json
# import time
# from utils.tuga_colors import G, Y, R, W
#
#
# class TugaServiceProbe:
#
#     def __init__(self, input_file, output_dir, concurrency=50, timeout=6, retries=2, verbose=False):
#         self.input_file = input_file
#         self.output_dir = output_dir
#         self.concurrency = concurrency
#         self.timeout = timeout
#         self.retries = retries
#         self.verbose = verbose
#
#         self.web_hosts = []
#         self.dead_hosts = []
#         self.services = []
#
#         os.makedirs(self.output_dir, exist_ok=True)
#
#     # --------------------------------------------------------------------------------------------------
#     def load_hosts(self):
#         hosts = []
#         with open(self.input_file) as f:
#             for line in f:
#                 h = line.strip().split("\t")[0]
#                 if h:
#                     hosts.append(h)
#         return hosts
#
#     # --------------------------------------------------------------------------------------------------
#     async def probe_host(self, client, host):
#         """Tenta HTTPS e depois HTTP, com retries."""
#         for attempt in range(1, self.retries + 2):
#             for scheme in ["https", "http"]:
#                 url = f"{scheme}://{host}"
#                 try:
#                     r = await client.get(url, follow_redirects=True)
#                     service = {
#                         "host": host,
#                         "url": str(r.url),
#                         "status": r.status_code,
#                         "title": self.extract_title(r.text),
#                         "server": r.headers.get("server", ""),
#                         "scheme": scheme,
#                         "redirected": str(r.url) != url
#                     }
#                     return service
#                 except httpx.RequestError:
#                     continue  # tenta próxima scheme ou retry
#             await asyncio.sleep(0.1)  # pequena pausa entre retries
#         return None  # todas tentativas falharam
#
#     # --------------------------------------------------------------------------------------------------
#     def extract_title(self, html):
#         if not html:
#             return ""
#         html_lower = html.lower()
#         start = html_lower.find("<title>")
#         end = html_lower.find("</title>")
#         if start != -1 and end != -1:
#             return html[start+7:end].strip()
#         return ""
#
#     # --------------------------------------------------------------------------------------------------
#     async def run_async(self, hosts):
#         limits = httpx.Limits(max_connections=self.concurrency)
#         timeout = httpx.Timeout(self.timeout)
#
#         async with httpx.AsyncClient(limits=limits, timeout=timeout, verify=False) as client:
#             sem = asyncio.Semaphore(self.concurrency)
#
#             async def bound_probe(host):
#                 async with sem:
#                     try:
#                         result = await self.probe_host(client, host)
#                         return host, result
#                     except Exception:
#                         return host, None
#
#             tasks = [bound_probe(h) for h in hosts]
#
#             total = len(hosts)
#             processed = 0
#
#             for coro in asyncio.as_completed(tasks):
#                 host, result = await coro
#
#                 processed += 1
#                 if not self.verbose and processed % 50 == 0:
#                     print(Y + f"[*] Probed {processed}/{total} hosts..." + W, end="\r")
#
#                 if result:
#                     self.services.append(result)
#                     self.web_hosts.append(host)
#                     if self.verbose:
#                         print(G + f"[+] {host} → {result['status']} {result['scheme']} {result['title']}" + W)
#
#                 else:
#                     self.dead_hosts.append(host)
#                     if self.verbose:
#                         print(R + f"[-] {host} dead" + W)
#
#                 if not self.verbose:
#                     print()
#
#     # --------------------------------------------------------------------------------------------------
#     def save_results(self):
#         services_path = os.path.join(self.output_dir, "services.json")
#         webhosts_path = os.path.join(self.output_dir, "web_hosts.txt")
#         deadhosts_path = os.path.join(self.output_dir, "dead_hosts.txt")
#
#         with open(services_path, "w") as f:
#             json.dump(self.services, f, indent=2)
#
#         with open(webhosts_path, "w") as f:
#             for h in sorted(set(self.web_hosts)):
#                 f.write(h + "\n")
#
#         with open(deadhosts_path, "w") as f:
#             for h in sorted(set(self.dead_hosts)):
#                 f.write(h + "\n")
#
#         print(G + f"[+] Saved {len(self.services)} services" + W)
#
#     # --------------------------------------------------------------------------------------------------
#     def run(self):
#         print(Y + "[*] Loading hosts..." + W)
#         hosts = self.load_hosts()
#         print(Y + f"[*] Probing {len(hosts)} hosts..." + W)
#
#         start = time.time()
#
#         try:
#             asyncio.run(self.run_async(hosts))
#         except Exception as e:
#             print(R + f"[!] Probe crashed: {e}" + W)
#
#         self.save_results()
#
#         print(G + f"\n[+] Probe completed in {time.time() - start:.2f}s" + W)
#         print(G + f"[+] Results saved in: {self.output_dir}" + W)
#
