# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import ssl
import socket
import json
import os
from datetime import datetime, timezone
import traceback

TIMEOUT = 5
RETRIES = 2

# Ciphers/versions considered weak
WEAK_TLS_VERSIONS = {"TLSv1", "TLSv1.1"}
WEAK_CIPHERS = {"RC4", "DES", "3DES", "MD5"}

# ----------------------------------------------------------------------------------------------------------
# TLS reaction for enterprise/ICS environments
# Captures certificate details, TLS version, cipher, and weak flags
# ----------------------------------------------------------------------------------------------------------
def run_tls_reaction(subdomain: str, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "tls.json")

    for attempt in range(1, RETRIES + 1):
        result = {
            "hostname": subdomain,
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
            "tls_version": None,
            "cipher": None,
            "cert": {},
            "weak_flags": [],
            "attempt": attempt,
            "error": None
        }

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((subdomain, 443), timeout=TIMEOUT) as sock:
                with context.wrap_socket(sock, server_hostname=subdomain) as ssock:
                    result["tls_version"] = ssock.version()
                    result["cipher"] = ssock.cipher()[0]

                    # Weak TLS / cipher checks
                    if result["tls_version"] in WEAK_TLS_VERSIONS:
                        result["weak_flags"].append("WEAK_TLS_VERSION")
                    if any(bad in result["cipher"] for bad in WEAK_CIPHERS):
                        result["weak_flags"].append("WEAK_CIPHER")

                    # Certificate extraction
                    cert = ssock.getpeercert()
                    if cert:
                        not_before = cert.get("notBefore")
                        not_after = cert.get("notAfter")
                        subject = dict(x[0] for x in cert.get("subject", []))
                        issuer = dict(x[0] for x in cert.get("issuer", []))
                        result["cert"] = {
                            "subject": subject,
                            "issuer": issuer,
                            "not_before": not_before,
                            "not_after": not_after,
                            "days_remaining": None
                        }

                        if not_after:
                            try:
                                expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                                days_left = (expires - datetime.utcnow().replace(tzinfo=timezone.utc)).days
                                result["cert"]["days_remaining"] = days_left
                                if days_left < 30:
                                    result["weak_flags"].append("CERT_EXPIRING_SOON")
                            except Exception:
                                result["cert"]["parse_error"] = "Could not parse certificate date"

            # Save and exit after successful attempt
            with open(out_file, "w") as f:
                json.dump(result, f, indent=2)
            return result

        except Exception as e:
            result["error"] = str(e)
            with open(os.path.join(output_dir, "tls_error.log"), "a") as f:
                f.write(traceback.format_exc() + "\n")

    # If all retries fail, save last attempt
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    return result

