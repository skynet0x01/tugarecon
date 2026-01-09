#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2026

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2026 skynet0x01
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.

# import go here
# ----------------------------------------------------------------------------------------------------------
import dns.resolver  # dnspython
import whois
# Import internal
from utils.tuga_colors import G, Y, B, R, W


# ----------------------------------------------------------------------------------------------------------
def DNS_Record_Types(target):
    print(G + "\n[+] DNS Record Types..." + W)
    print(G + "────────────────────────────────────────────────────────────" + W)

    record_types = ['A', 'AAAA', 'AFSDB', 'NS', 'CNAME', 'MX', 'PTR', 'SOA', 'CERT',
                    'HINFO', 'MINFO', 'TLSA', 'SPF', 'KEY', 'NXT', 'CAA', 'TXT', 'MD',
                    'NULL', 'DNAME', 'URI', 'DLV', 'APL', 'CSYNC', 'DHCID', 'LOC']

    for record in record_types:
        try:
            answer = dns.resolver.resolve(target, record)
            answer.timeout = 10
            print(Y + f'\nRecords: {record}' + W)
            print('-' * 30)
            for rdata in answer:
                print(rdata.to_text())
        #except dns.resolver.LifetimeTimeout:
            #pass
        except dns.resolver.NoAnswer:
            pass
        except dns.exception.Timeout:
            pass
        except dns.resolver.NoNameservers:
            pass
        except dns.resolver.NXDOMAIN:
            print(f'{target} does not exist.')
            print(G + "────────────────────────────────────────────────────────────\n" + W)
            quit()
        except KeyboardInterrupt:
            print("\nTugaRecon interrupted by user\n")
            quit()
    print("")
    print(G + "────────────────────────────────────────────────────────────" + W)
# ----------------------------------------------------------------------------------------------------------
def bscan_whois_look(target):
    try:
        dict = []
        domain = whois.query(target)
        data = domain.__dict__
        dict.append(data)
        print("Domain expiration: ", domain.expiration_date)
        print(G + "────────────────────────────────────────────────────────────\n" + W)
        for dict_line in dict:
            for k, v in dict_line.items():
                print(k + ": " + v)
        print(G + "────────────────────────────────────────────────────────────\n" + W)
        print("")
    except KeyboardInterrupt:
        print("\nTugaRecon interrupted by user\n")
        quit()
    except Exception as e:
        pass
    
    
# ----------------------------------------------------------------------------------------------------------
@staticmethod
def is_intranet(ip):
    ret = ip.split('.')
    if not len(ret) == 4:
        return True
    if ret[0] == '10':
        return True
    if ret[0] == '172' and 16 <= int(ret[1]) <= 32:
        return True
    if ret[0] == '192' and ret[1] == '168':
        return True
    return False
# ----------------------------------------------------------------------------------------------------------

