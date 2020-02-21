# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import go here

import os  # Miscellaneous operating system interfaces
import queue  # A synchronized queue class
import re  # Regular expression operations
import sys  # System-specific parameters and functions
import threading  # Thread-based parallelism
import time  # Time access and conversions
import dns.resolver  # dnspython

# Import internal

from functions import G, W, R, Y
from lib.console_terminal import getTerminalSize


##################################################################################################

class TugaBruteScan:
    def __init__(self, target, options):

        self.target = target
        self.options = options # default threads 300
        self.ignore_intranet = options.i  # need more options... not complete
        # set threads, count system
        self.thread_count = self.scan_count = self.found_count = 0
        self.lock = threading.RLock()
        # Resize console
        self.console_width = getTerminalSize()[0] - 2 # thanks guys
        self.msg_queue = queue.Queue()
        self.STOP_SCAN = False
        threading.Thread(target=self._print_msg).start()
        self._dns_queries()
        self._load_dns_servers()  # load DNS servers from a list
        # set resolver from dns.resolver
        self.resolvers = [dns.resolver.Resolver(configure=False) for _ in range(options.threads)]
        for _ in self.resolvers:
            _.lifetime = _.timeout = 10.0
        self._load_next_sub()
        self.queue = queue.PriorityQueue()
        t = threading.Thread(target=self._load_sub_names)
        t.start()
        while not self.queue.qsize() > 0 and t.is_alive():
            time.sleep(0.1)
            # save results in to a file
        if options.output:
            outfile = options.output
        else:
            outfile = 'results/' + target + '_tugascan.txt' if not options.full_scan else 'results/' + target + '_tugascan_full.txt'
        self.outfile = open(outfile, 'w')
        # save ip ,dns.
        self.ip_dict = {}
        self.last_scanned = time.time()
        self.ex_resolver = dns.resolver.Resolver(configure=False)
        self.start_time = None

    ###############################################################################################

    def _load_dns_servers(self):
        # dns_servers.txt
        print(G + '[+] Initializing, validate DNS servers ...')
        self.dns_servers = []
        with open('wordlist/dns_servers.txt') as f:
            for line in f:
                server = line.strip()
                if not server:
                    continue
                while True:
                    if threading.activeCount() < 50:
                        t = threading.Thread(target=self._test_server, args=(server,))
                        t.start()
                        break
                    else:
                        time.sleep(0.1)

        while threading.activeCount() > 2:
            time.sleep(0.1)
        self.dns_count = len(self.dns_servers) # count the number of DNS servers
        sys.stdout.write('\n')
        print('[+] Found %s available DNS Servers' % self.dns_count)
        if self.dns_count == 0:
            print('[ERROR] Oops! No DNS Servers available.')
            self.STOP_SCAN = True
            sys.exit(-1)

    ###############################################################################################

    def _dns_queries(self):
        print(Y + "TugaRecon, tribute to Portuguese explorers reminding glorious past of this country\n" + W)
        print(G + "\n[+] DNS queries...\n" + W)
        print(G + "**************************************************************\n" + W)
        for qtype in 'A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CERT', 'HINFO', 'MINFO', 'TLSA', 'SPF':
            answer = dns.resolver.query(self.target, qtype, raise_on_no_answer=False)
            if answer.rrset is not None:
                print(answer.rrset, '\n')
            else:
                pass
        print(G + "**************************************************************\n" + W)

    ###############################################################################################

    def _test_server(self, server):
        resolver = dns.resolver.Resolver(configure=False)
        resolver.lifetime = resolver.timeout = 5.0
        try:
            resolver.nameservers = [server]
            answers = resolver.query('s-coco-ns01.co-co.nl')  # test lookup a existed domain
            if answers[0].address != '188.122.89.156':
                raise Exception('incorrect DNS response')
            try:
                resolver.query('test.bad.dns.lordneostark.pt')  # Non-existed domain test
                with open('wordlist/bad_dns_servers.txt', 'a') as f:
                    f.write(server + '\n')
                self.msg_queue.put('[+] Bad DNS Server found %s' % server)
            except:
                self.dns_servers.append(server)
            self.msg_queue.put('[+] Check DNS Server %s < OK >   Found %s' % (server.ljust(16), len(self.dns_servers)))
        except:
            self.msg_queue.put('[+] Check DNS Server %s <Fail>   Found %s' % (server.ljust(16), len(self.dns_servers)))

    ###############################################################################################

    def _load_sub_names(self):
        self.msg_queue.put('[+] Load first list...\n' + W)
        if self.options.full_scan and self.options.file == 'subdomains.txt':
            _file = 'wordlist/subdomains_full.txt'
        else:
            if os.path.exists(self.options.file):
                _file = self.options.file
            elif os.path.exists('wordlist/%s' % self.options.file):
                _file = 'wordlist/%s' % self.options.file
            else:
                self.msg_queue.put('[ERROR] Oops! Names file not exists: %s' % self.options.file)
                return

        normal_lines = []
        wildcard_lines = []
        wildcard_list = []
        regex_list = []
        lines = set()

        with open(_file) as f:
            for line in f:
                sub = line.strip()
                if not sub or sub in lines:
                    continue
                lines.add(sub)
                #print(lines) # linha para testes e debug, remover linha no final

                if sub.find('{alphnum}') >= 0 or sub.find('{alpha}') >= 0 or sub.find('{num}') >= 0:
                    wildcard_lines.append(sub)
                    sub = sub.replace('{alphnum}', '[a-z0-9]')
                    sub = sub.replace('{alpha}', '[a-z]')
                    sub = sub.replace('{num}', '[0-9]')
                    if sub not in wildcard_list:
                        wildcard_list.append(sub)
                        regex_list.append('^' + sub + '$')
                        #print("teste", regex_list.append('^' + sub + '$'))
                else:
                    normal_lines.append(sub)
        pattern = '|'.join(regex_list)
        if pattern:
            _regex = re.compile(pattern)
            if _regex:
                for line in normal_lines:
                    if _regex.search(line):
                        normal_lines.remove(line)

        lst_subs = []
        GROUP_SIZE = 1 if not self.options.full_scan else 1  # disable scan by groups

        for item in normal_lines:
            lst_subs.append(item)
            if len(lst_subs) >= GROUP_SIZE:
                self.queue.put(lst_subs)
                lst_subs = []

        sub_queue = queue.LifoQueue()
        for line in wildcard_lines:
            sub_queue.put(line)
            while sub_queue.qsize() > 0:
                item = sub_queue.get()
                if item.find('{alphnum}') >= 0:
                    for _letter in 'abcdefghijklmnopqrstuvwxyz0123456789':
                        sub_queue.put(item.replace('{alphnum}', _letter, 1))
                elif item.find('{alpha}') >= 0:
                    for _letter in 'abcdefghijklmnopqrstuvwxyz':
                        sub_queue.put(item.replace('{alpha}', _letter, 1))
                elif item.find('{num}') >= 0:
                    for _letter in '0123456789':
                        sub_queue.put(item.replace('{num}', _letter, 1))
                else:
                    lst_subs.append(item)
                    if len(lst_subs) >= GROUP_SIZE:
                        while self.queue.qsize() > 10000:
                            time.sleep(0.1)
                        self.queue.put(lst_subs)
                        lst_subs = []

        if lst_subs:
            self.queue.put(lst_subs)

    ###############################################################################################

    def _load_next_sub(self):
        self.msg_queue.put('[+] Load second list ...')
        next_subs = []

        _file = 'wordlist/next_subdomains.txt' if not self.options.full_scan else 'wordlist/next_subdomains_full.txt'

        with open(_file) as f:
            for line in f:
                sub = line.strip()
                if sub and sub not in next_subs:
                    tmp_set = {sub}
                    while len(tmp_set) > 0:
                        item = tmp_set.pop()
                        if item.find('{alphnum}') >= 0:
                            for _letter in 'abcdefghijklmnopqrstuvwxyz0123456789':
                                tmp_set.add(item.replace('{alphnum}', _letter, 1))
                        elif item.find('{alpha}') >= 0:
                            for _letter in 'abcdefghijklmnopqrstuvwxyz':
                                tmp_set.add(item.replace('{alpha}', _letter, 1))
                        elif item.find('{num}') >= 0:
                            for _letter in '0123456789':
                                tmp_set.add(item.replace('{num}', _letter, 1))
                        elif item not in next_subs:
                            next_subs.append(item)
        self.next_subs = next_subs

    ###############################################################################################

    def _update_scan_count(self):
        self.last_scanned = time.time()
        self.scan_count += 1

    ###############################################################################################

    def _update_found_count(self):
        # no need to use a lock
        self.found_count += 1

    ###############################################################################################

    def _print_msg(self):
        while not self.STOP_SCAN:
            try:
                _msg = self.msg_queue.get(timeout=0.1)
            except:
                continue

            if _msg == 'status':
                msg = 'Found %s subdomains | %s groups left | %s scanned in %.1f seconds| %s threads' % (
                    self.found_count, self.queue.qsize(), self.scan_count, time.time() - self.start_time,
                    self.thread_count)
                sys.stdout.write('\r' + ' ' * (self.console_width - len(msg)) + msg)
            elif _msg.startswith('[+] Check DNS Server'):
                sys.stdout.write('\r' + _msg + ' ' * (self.console_width - len(_msg)))
            else:
                sys.stdout.write('\r' + _msg + ' ' * (self.console_width - len(_msg)) + '\n')
            sys.stdout.flush()

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

    def _scan(self):
        thread_id = int(threading.currentThread().getName())
        self.resolvers[thread_id].nameservers = [self.dns_servers[thread_id % self.dns_count]]

        _lst_subs = []
        self.lock.acquire()
        self.thread_count += 1
        self.lock.release()

        while not self.STOP_SCAN:
            if not _lst_subs:
                try:
                    _lst_subs = self.queue.get(timeout=0.1)
                except:
                    if time.time() - self.last_scanned > 2.0:
                        break
                    else:
                        continue
            sub = _lst_subs.pop()
            _sub = sub.split('.')[-1]
            _sub_timeout_count = 0
            while not self.STOP_SCAN:
                try:
                    cur_sub_domain = sub + '.' + self.target
                    self._update_scan_count()
                    self.msg_queue.put('status')
                    try:
                        answers = self.resolvers[thread_id].query(cur_sub_domain)
                    except dns.resolver.NoAnswer as e:
                        answers = self.ex_resolver.query(cur_sub_domain)
                    is_wildcard_record = False
                    if answers:
                        ips = ', '.join(sorted([answer.address for answer in answers]))
                        if ips in ['1.1.1.1', '127.0.0.1', '0.0.0.0']:
                            break

                        if (_sub, ips) not in self.ip_dict:
                            self.ip_dict[(_sub, ips)] = 1
                        else:
                            self.ip_dict[(_sub, ips)] += 1

                        if ips not in self.ip_dict:
                            self.ip_dict[ips] = 1
                        else:
                            self.ip_dict[ips] += 1

                        if self.ip_dict[(_sub, ips)] > 3 or self.ip_dict[ips] > 6:
                            is_wildcard_record = True

                        if is_wildcard_record:
                            break

                        if (not self.ignore_intranet) or (not TugaBruteScan.is_intranet(answers[0].address)):
                            self._update_found_count()
                            msg = cur_sub_domain.ljust(30) + ips
                            self.msg_queue.put(msg)
                            self.msg_queue.put('status')
                            self.outfile.write(cur_sub_domain.ljust(30) + '\t' + ips + '\n')
                            self.outfile.flush()

                            try:
                                self.resolvers[thread_id].query('lordneostark.' + cur_sub_domain)
                            except dns.resolver.NXDOMAIN as e:
                                _lst = []
                                if_put_one = (self.queue.qsize() < self.dns_count * 5)
                                for i in self.next_subs:
                                    _lst.append(i + '.' + sub)
                                    if if_put_one:
                                        self.queue.put(_lst)
                                        _lst = []
                                    elif len(_lst) >= 10:
                                        self.queue.put(_lst)
                                        _lst = []
                                if _lst:
                                    self.queue.put(_lst)
                            except:
                                pass
                        break
                except (dns.resolver.NXDOMAIN, dns.name.EmptyLabel) as e:
                    break
                except (dns.resolver.NoNameservers, dns.resolver.NoAnswer, dns.exception.Timeout) as e:
                    _sub_timeout_count += 1
                    if _sub_timeout_count >= 6:  # give up
                        break
                except Exception as e:
                    with open('errors.log', 'a') as errFile:
                        errFile.write('%s [%s] %s %s\n' % (threading.current_thread, type(e), cur_sub_domain, e))
                    break
        self.lock.acquire()
        self.thread_count -= 1
        self.lock.release()
        self.msg_queue.put('status')

    ###############################################################################################

    def run(self):
        self.start_time = time.time()
        for i in range(self.options.threads):
            try:
                t = threading.Thread(target=self._scan, name=str(i))
                t.setDaemon(True)
                t.start()
            except:
                pass
        while self.thread_count > 0:
            try:
                time.sleep(1.0)
            except KeyboardInterrupt as e:
                msg = (R + '[WARNING] User aborted, wait all slave threads to exit...' + W)
                sys.stdout.write('\r' + msg + ' ' * (self.console_width - len(msg)) + '\n\r')
                sys.stdout.flush()
                self.STOP_SCAN = True
        self.STOP_SCAN = True

###############################################################################################
