# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
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
    print(G + "\n[+] WHOIS Lookup..." + W)
    print(G + "────────────────────────────────────────────────────────────\n" + W)
    try:
        records = []

        domain = whois.query(target)

        data = domain.__dict__
        records.append(data)
        print("Domain expiration: ", domain.expiration_date)
        print(G + "────────────────────────────────────────────────────────────\n" + W)
        for records_line in records:
            for k, v in domain.__dict__.items():
                print(B + f"{k}:" + W)

                if isinstance(v, list):
                    for item in v:
                        print(f"  - {item}")
                else:
                    print(f"  {v}")

                print("")


        print(G + "────────────────────────────────────────────────────────────\n" + W)
        print("")

    except KeyboardInterrupt:
        print("\nTugaRecon interrupted by user\n")
        quit()

    except Exception as e:
        print(R + f"[WHOIS] Failed for {target}: {e}" + W)

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

