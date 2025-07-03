# TugaRecon - DNS, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
import dns.resolver  # dnspython
import whois
# Import internal
from utils.tuga_colors import G, Y, B, R, W


# ----------------------------------------------------------------------------------------------------------
def DNS_Record_Types(target):
    print(G + "\n[+] DNS Record Types..." + W)
    print(G + "**************************************************************" + W)

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
            print(G + "**************************************************************\n" + W)
            quit()
        except KeyboardInterrupt:
            print("\nTugaRecon interrupted by user\n")
            quit()
    print(G + "**************************************************************" + W)
# ----------------------------------------------------------------------------------------------------------
def bscan_whois_look(target):
    try:
        dict = []
        domain = whois.query(target)
        data = domain.__dict__
        dict.append(data)
        #print(domain.__dict__, "\n")
        #print(domain.name, "\n")
        print("Domain expiration: ", domain.expiration_date)
        print(G + "**************************************************************\n" + W)
        for dict_line in dict:
            for k, v in dict_line.items():
                print(k + ": " + v)
        print(G + "**************************************************************\n" + W)
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

