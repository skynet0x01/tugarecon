# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import go here

import requests
import signal
import os
import sys
import time
from threading import Thread  # Thread-based parallelism
from queue import Queue  # A synchronized queue class

# internal functions
from functions import G, W

queue = Queue()


def scan_subdomains(domain):
    global queue

    while True:
        # get the subdomain from the queue
        subdomain = queue.get()
        # scan the subdomain from txt file
        sys.stdout.write(G + 'Testing subdomains: '+ str(subdomain) +'                                       \r' +W)
        #print(str(subdomain), end="\r", flush=True)
        sys.stdout.flush()

        url = f"http://{subdomain}.{domain}"

        try:
            requests.get(url, allow_redirects=False)
        except requests.ConnectionError:
            pass
        else:
            print("[+] Discovered subdomain:", url)

        # we're done with scanning that subdomain
        queue.task_done()


# exit handler for signals.  So ctrl+c will work.
# The 'multiprocessing' library each process is it's own process which side-steps the GIL
# If the user wants to exit prematurely,  each process must be killed.
def killproc(signum=0, frame=0, pid=False):
    if not pid:
        pid = os.getpid()
        os.kill(pid, 9)


# Every 'multiprocessing' process needs a signal handler.
# All processes need to die, we don't want to leave zombies.
def signal_init():
    # Escliate signal to prevent zombies.
    signal.signal(signal.SIGINT, killproc)
    try:
        signal.signal(signal.SIGTSTP, killproc)
        signal.signal(signal.SIGQUIT, killproc)
    except:
        # Windows
        pass


def main(domain, n_threads, subdomains):
    global queue
    signal_init()

    # fill the queue with all the subdomains
    for subdomain in subdomains:
        queue.put(subdomain)

    for t in range(n_threads):
        # start all threads
        worker = Thread(target=scan_subdomains, args=(domain,))
        # daemon thread means a thread that will end when the main thread ends
        worker.daemon = True
        worker.start()

    queue.join()
