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
from datetime import datetime

TIMEOUT = 5


def run_tls_reaction(subdomain, output_dir):
    result = {
        "hostname": subdomain,
        "timestamp": datetime.utcnow().isoformat(),
        "tls_version": None,
        "cipher": None,
        "cert": {},
        "weak_flags": []
    }

    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((subdomain, 443), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=subdomain) as ssock:
                result["tls_version"] = ssock.version()
                result["cipher"] = ssock.cipher()[0]

                cert = ssock.getpeercert()
                if cert:
                    not_before = cert.get("notBefore")
                    not_after = cert.get("notAfter")

                    result["cert"] = {
                        "subject": dict(x[0] for x in cert.get("subject", [])),
                        "issuer": dict(x[0] for x in cert.get("issuer", [])),
                        "not_before": not_before,
                        "not_after": not_after
                    }

                    if not_after:
                        expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                        days_left = (expires - datetime.utcnow()).days
                        result["cert"]["days_remaining"] = days_left

                        if days_left < 30:
                            result["weak_flags"].append("CERT_EXPIRING_SOON")

                if result["tls_version"] in ("TLSv1", "TLSv1.1"):
                    result["weak_flags"].append("WEAK_TLS_VERSION")

    except Exception as e:
        result["error"] = str(e)

    # persistência
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "tls.json")

    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)

    return result
