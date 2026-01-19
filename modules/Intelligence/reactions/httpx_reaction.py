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
import os
import traceback

# ----------------------------------------------------------------------------------------------------------
# HTTP/HTTPS probing reaction
# Enterprise/ICS aware, captures headers, status, redirects and errors
# ----------------------------------------------------------------------------------------------------------
def run_httpx(subdomain: str, output_dir: str, retries: int = 2, timeout: int = 10):
    """
    Perform HTTP/HTTPS request for a given subdomain.
    Stores detailed JSON output in the output directory.
    """
    urls = [f"https://{subdomain}", f"http://{subdomain}"]
    results = []

    for url in urls:
        attempt = 0
        success = False

        while attempt <= retries and not success:
            attempt += 1
            try:
                with httpx.Client(follow_redirects=True, timeout=timeout) as client:
                    r = client.get(url)
                    result = {
                        "url": url,
                        "status": r.status_code,
                        "headers": dict(r.headers),
                        "redirects": [str(h.url) for h in r.history],
                        "attempt": attempt,
                        "error": None,
                    }
                    results.append(result)
                    success = True
            except Exception as e:
                result = {
                    "url": url,
                    "status": None,
                    "headers": {},
                    "redirects": [],
                    "attempt": attempt,
                    "error": str(e),
                }
                results.append(result)
                # Save detailed traceback for debugging
                with open(os.path.join(output_dir, "httpx_error.log"), "a") as f:
                    f.write(traceback.format_exc() + "\n")

    # Save JSON output
    output_file = os.path.join(output_dir, "httpx.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)


