# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import requests
import json
import os
from datetime import datetime, timezone
import traceback

TIMEOUT = 8
RETRIES = 2

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]

# ----------------------------------------------------------------------------------------------------------
# Headers reaction for enterprise / OT / SCADA environments
# ----------------------------------------------------------------------------------------------------------
def run_headers(subdomain: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "headers.json")

    for attempt in range(1, RETRIES + 1):
        result = {
            "hostname": subdomain,
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "headers": {},
            "missing": [],
            "weak_flags": [],
            "attempt": attempt,
            "error": None
        }

        url = f"https://{subdomain}"

        try:
            r = requests.get(url, timeout=TIMEOUT, verify=False)

            for h in SECURITY_HEADERS:
                if h in r.headers:
                    result["headers"][h] = r.headers[h]
                else:
                    result["missing"].append(h)

            # Weakness checks
            if "Strict-Transport-Security" not in r.headers:
                result["weak_flags"].append("NO_HSTS")

            if "Content-Security-Policy" not in r.headers:
                result["weak_flags"].append("NO_CSP")

            if "X-Frame-Options" not in r.headers:
                result["weak_flags"].append("NO_X_FRAME")

            # Save and exit on success
            with open(out_file, "w") as f:
                json.dump(result, f, indent=2)
            return result

        except Exception as e:
            result["error"] = str(e)
            with open(os.path.join(output_dir, "headers_error.log"), "a") as f:
                f.write(traceback.format_exc() + "\n")

    # Save last attempt if all retries fail
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    return result

