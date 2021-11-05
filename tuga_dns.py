import dns.resolver  # dnspython
import whois

# Import internal
from functions import G, W, R, Y


###############################################################################################

def bscan_dns_queries(target):
    print(G + "\n[+] DNS queries...\n" + W)
    print(G + "**************************************************************\n" + W)
    try:
        for qtype in 'A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CERT', 'HINFO', 'MINFO', 'TLSA', 'SPF':
            answer = dns.resolver.query(target, qtype, raise_on_no_answer=False, lifetime=10)
            if answer.rrset is not None:
                print(answer.rrset, '\n')
            else:
                pass
    except Exception as e:
        pass
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
        #print("Domain expiration: ", domain.expiration_date, "\n")
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
