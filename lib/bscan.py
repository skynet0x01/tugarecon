import dns.resolver  # dnspython

# Import internal
from functions import G, W, R, Y

###############################################################################################

def _dns_queries(target):

    print(G + "\n[+] DNS queries...\n" + W)
    print(G + "**************************************************************\n" + W)
    for qtype in 'A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CERT', 'HINFO', 'MINFO', 'TLSA', 'SPF':
        answer = dns.resolver.query(target, qtype, raise_on_no_answer=False)
        if answer.rrset is not None:
            print(answer.rrset, '\n')
        else:
            pass
    print(G + "**************************************************************\n" + W)

###############################################################################################

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