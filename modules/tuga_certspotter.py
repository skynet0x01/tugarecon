# TugaRecon - certspotter, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# ----------------------------------------------------------------------------------------------------------
# import modules
import time
import requests
import json

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import internal functions
from utils.tuga_functions import write_file
#from utils.tuga_functions import DeleteDuplicate
#from utils.tuga_colors import G, Y, B, R, W

# ----------------------------------------------------------------------------------------------------------
class Certspotter:

    def __init__(self, target):

        self.target = target
        self.module_name = "CertSpotter"
        self.engine = "certspotter"
        self.response = self.engine_url()

        if self.response != 1:
            self.enumerate(self.response, target) # Call the function enumerate
        else:
            pass
        
        
# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        try:
            response = requests.get(f'https://api.certspotter.com/v1/issuances?domain={self.target}&include_subdomains=true&expand=dns_names').text
        except (requests.ConnectionError, requests.Timeout) as exception:
            response = 1
        return response
    
    
# ----------------------------------------------------------------------------------------------------------
    def enumerate(self, response, target):
        subdomains = []
        subdomainscount = 0
        start_time = time.time()
        #################################
        try:
            extract_sub = json.loads(response)
            for i in extract_sub:
                subdomainscount = subdomainscount + 1
                subdomains = i['dns_names'][0]
                #print(f"    [*] {subdomains}")
                write_file(subdomains, target)
        except Exception as e:
            pass
# ----------------------------------------------------------------------------------------------------------

