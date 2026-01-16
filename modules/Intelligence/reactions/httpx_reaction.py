# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import httpx
import json

def run_httpx(subdomain, output_dir):
    url = f"https://{subdomain}"

    result = {
        "url": url,
        "status": None,
        "headers": {},
        "redirects": [],
    }

    with httpx.Client(follow_redirects=True, timeout=10) as client:
        r = client.get(url)
        result["status"] = r.status_code
        result["headers"] = dict(r.headers)
        result["redirects"] = [str(h.url) for h in r.history]

    with open(f"{output_dir}/httpx.json", "w") as f:
        json.dump(result, f, indent=2)

