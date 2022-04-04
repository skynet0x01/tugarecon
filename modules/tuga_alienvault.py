# TugaRecon - crt module, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# import modules
import time
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import internal modules
from modules import tuga_useragents #random user-agent
# Import internal functions
from utils.tuga_functions import write_file
from utils.tuga_functions import DeleteDuplicate
from utils.tuga_colors import G, Y, B, R, W
################################################################################
class Alienvault:
    def __init__(self, target):
        self.target = target
        self.module_name = "Alienvault"
        self.engine = "alienvault"
        self.response = self.engine_url() # URL

        if self.response != 1:
            self.enumerate(self.response, target) # Call the function enumerate
        else:
            pass
################################################################################
    def engine_url(self):
        try:
            response = requests.get(f'https://otx.alienvault.com/api/v1/indicators/domain/{self.target}/passive_dns').text
            return response
        except requests.ConnectionError:
            response = 1
            return response
################################################################################
    def enumerate(self, response, target):
        subdomains = []
        self.subdomainscount = 0
        start_time = time.time()
        #################################
        try:
            extract_sub = json.loads(response)
            #print(extract_sub)
            for i in extract_sub['passive_dns']:
                subdomains = i['hostname']
                self.subdomainscount = self.subdomainscount + 1
                #print(f"    [*] {subdomains}")
                write_file(subdomains, target)
        except Exception as e:
            pass
        #################################
