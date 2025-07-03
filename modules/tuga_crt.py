# TugaRecon - crt module, write by skynet0x01
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

# Import internal modules
from modules import tuga_useragents #random user-agent
# Import internal functions
from utils.tuga_functions import write_file
#from utils.tuga_functions import DeleteDuplicate
#from utils.tuga_colors import G, Y, B, R, W


# ----------------------------------------------------------------------------------------------------------
class CRT:

    def __init__(self, target):

        self.target = target
        self.module_name = "SSL Certificates"
        self.engine = "crt"
        self.response = self.engine_url() # URL

        if self.response != 1:
            self.enumerate(self.response, target) # Call the function enumerate
        else:
            pass
        
        
# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        try:
            response = requests.get(f'https://crt.sh/?q={self.target}&output=json').text
            return response
        except requests.ConnectionError:
            response = 1
            return response
        
        
# ----------------------------------------------------------------------------------------------------------
    def enumerate(self, response, target):
        subdomains = []
        self.subdomainscount = 0
        start_time = time.time()
        #################################
        try:
            extract_sub = json.loads(response)
            #print(extract_sub)
            for i in extract_sub:
                self.subdomainscount = self.subdomainscount + 1
                #subdomains = response.json()[self.subdomainscount]["name_value"]
                subdomains = i['name_value']
                #print(f"{subdomains}")

                write_file(subdomains, target)
        except Exception as e:
            pass
# ----------------------------------------------------------------------------------------------------------

