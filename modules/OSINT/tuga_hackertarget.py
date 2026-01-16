# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import time
import requests
import urllib3

from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

# Import internal functions
from utils.tuga_save import write_file


# ----------------------------------------------------------------------------------------------------------
class Hackertarget:

    def __init__(self, target):

        self.target = target
        self.module_name = "HackerTarget"
        self.engine = "hackertarget"
        self.response = self.engine_url()

        if self.response != 1:
            self.enumerate(self.response, target) # Call the function enumerate
        else:
            pass
        
        
# ----------------------------------------------------------------------------------------------------------
    def engine_url(self):
        try:
            response = requests.get(f"https://api.hackertarget.com/hostsearch/?q={self.target}").text
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
            extract_sub = response.split("\n")
            #print(extract_sub)
            for i in extract_sub:
                if "API count exceeded " in i:
                    pass
                else:
                    filters = i.split(",")
                    subdomains = filters[0]
                    #print(f"    [*] {subdomains}")
                    write_file(subdomains, target)
        except Exception as e:
            pass
# ----------------------------------------------------------------------------------------------------------

