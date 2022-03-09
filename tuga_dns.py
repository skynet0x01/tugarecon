import dns.resolver  # dnspython
import whois
# Import internal
from functions import G, W, R, Y
###############################################################################################
def DNS_Record_Types(target):
    print(G + "\n[+] DNS Record Types..." + W)
    print(G + "**************************************************************" + W)

    record_types = ['A', 'AAAA', 'NS', 'CNAME', 'MX', 'PTR', 'SOA', 'TXT', 'CERT', 'HINFO', 'MINFO', 'TLSA', 'SPF', 'KEY', 'NXT']
    for records in record_types:
        try:
            answer = dns.resolver.resolve(target, records)
            print(f'\nRecords: {records}')
            print('-' * 30)
            for server in answer:
                print(server.to_text())
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            print(f'{target} does not exist.')
            print(G + "**************************************************************\n" + W)
            quit()
        except KeyboardInterrupt:
            print('Quitting.')
            quit()
    print(G + "**************************************************************\n" + W)
###############################################################################################
def bscan_whois_look(target):
    try:
        dict = []
        domain = whois.query(target)
        data = domain.__dict__
        dict.append(data)
        #print(domain.__dict__, "\n")
        #print(domain.name, "\n")
        print("Domain expiration: ", domain.expiration_date, "\n")
        print(G + "**************************************************************\n" + W)
        for dict_line in dict:
            for k, v in dict_line.items():
                print(k + ": " + v)
        print(G + "**************************************************************\n" + W)
    except Exception as e:
        pass
###############################################################################################
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
###############################################################################################
