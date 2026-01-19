# --------------------------------------------------------------------------------------------------
# TugaRecon – Certificate Module
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# --------------------------------------------------------------------------------------------------

import ssl
import socket
import asyncio
from cryptography import x509
from cryptography.hazmat.backends import default_backend

# --------------------------------------------------------------------------------------------------
def fetch_cert_sync(host, port=443, timeout=5):
    """
    Fetch the DER-encoded certificate for a host.
    """
    try:
        ctx = ssl.create_default_context()
        if hasattr(ssl,"TLSVersion"):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        else:
            ctx.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        with socket.create_connection((host,port),timeout=timeout) as sock:
            with ctx.wrap_socket(sock,server_hostname=host) as ss:
                return ss.getpeercert(binary_form=True)
    except Exception:
        return None

# --------------------------------------------------------------------------------------------------
async def fetch_certs_for_hosts(hosts_list, concurrency=40, timeout=5):
    """
    Async fetch of certificates for multiple hosts.
    Returns a dict: {host: [SANs]}
    """
    cert_map_local = {}
    sem = asyncio.Semaphore(concurrency)

    async def worker(host):
        async with sem:
            der = await asyncio.to_thread(fetch_cert_sync, host, 443, timeout)
            sans = []
            if der:
                try:
                    cert = x509.load_der_x509_certificate(der, default_backend())
                    ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    sans.extend(ext.value.get_values_for_type(x509.DNSName))
                    cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value
                    if cn and cn not in sans: sans.append(cn)
                except Exception:
                    pass
            cert_map_local[host] = sans

    tasks = [worker(h) for h in hosts_list]
    await asyncio.gather(*tasks, return_exceptions=True)
    return cert_map_local
