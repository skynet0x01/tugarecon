# --------------------------------------------------------------------------------------------------
# TugaRecon – ASN & Network Info Module
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# --------------------------------------------------------------------------------------------------

import asyncio
import ipaddress
from ipwhois import IPWhois

# Simple in-memory cache
rdap_cache = {}

# --------------------------------------------------------------------------------------------------
async def prefetch_network_info(ip_set, concurrency=20):
    """
    Async RDAP lookup for a set of IPs with concurrency control.
    Results are cached in rdap_cache.
    """
    sem = asyncio.Semaphore(concurrency)

    async def lookup(ip):
        async with sem:
            if ip in rdap_cache:
                return
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    rdap_cache[ip] = {'asn':'Private Network','asn_description':'Private Network',
                                      'country':'N/A','cidr':'N/A','org':'Local/Internal'}
                    return
            except Exception:
                rdap_cache[ip] = {'asn':'Invalid','asn_description':'Invalid IP','country':'N/A','cidr':'N/A','org':'N/A'}
                return
            try:
                obj = IPWhois(ip)
                res = await asyncio.to_thread(obj.lookup_rdap)
                asn = res.get('asn') or 'Unknown'
                asn_desc = res.get('asn_description') or asn
                country = res.get('asn_country_code') or '??'
                cidr = res.get('network',{}).get('cidr') or 'Unknown'
                org = res.get('network',{}).get('name') or 'Unknown Org'
                rdap_cache[ip] = {'asn':asn,'asn_description':asn_desc,'country':country,'cidr':cidr,'org':org}
            except Exception:
                rdap_cache[ip] = {'asn':'Unknown','asn_description':'RDAP error','country':'??','cidr':'Unknown','org':'Unknown Org'}

    tasks = [lookup(ip) for ip in ip_set]
    await asyncio.gather(*tasks, return_exceptions=True)

# --------------------------------------------------------------------------------------------------
def get_network_info(ip):
    """
    Return cached RDAP info for a single IP.
    """
    return rdap_cache.get(ip, {'asn':'Unknown','asn_description':'Unknown ASN',
                               'country':'??','cidr':'Unknown','org':'Unknown Org'})
