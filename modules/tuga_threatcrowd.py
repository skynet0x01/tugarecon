# TugaRecon - threatcrowd, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# import modules
################################################################################
import time
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import internal modules
from modules import tuga_useragents #random user-agent
# Import internal functions
from functions import write_file
from functions import DeleteDuplicate
from functions import G, W
################################################################################
class Threatcrowd:

    def __init__(self, target):
        self.target = target
        self.module_name = "Threat Crowd"
        self.engine = "threatcrowd"
        self.response = self.engine_url()

        if self.response != 1:
            self.enumerate(self.response, target) # Call the function enumerate
        else:
            pass
################################################################################
    def engine_url(self):
        try:
            response = requests.get(f'https://threatcrowd.org/searchApi/v2/domain/report/?domain={self.target}').text
            return response
        except requests.ConnectionError:
            response = 1
            return response
################################################################################
    def enumerate(self, response, target):
        subdomains = []
        subdomainscount = 0
        start_time = time.time()
        #################################
        try:
            extract_sub = json.loads(response)
            #print(extract_sub)
            for i in extract_sub['subdomains']:
                self.subdomainscount = self.subdomainscount + 1
                #subdomains = response.json()[self.subdomainscount]["name_value"]
                subdomains = i
                #print(f"    [*] {subdomains}")
                write_file(subdomains, target)
        except Exception as e:
            pass
                #################################
