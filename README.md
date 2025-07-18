# TugaRecon
<a href="https://github.com/skynet0x01/tugarecon/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/skynet0x01/tugarecon?style=for-the-badge"></a>
<a href="https://github.com/skynet0x01/tugarecon/network"><img alt="GitHub forks" src="https://img.shields.io/github/forks/skynet0x01/tugarecon?style=for-the-badge"></a>
<a href="https://github.com/skynet0x01/tugarecon/blob/master/LICENSE"><img alt="GitHub license" src="https://img.shields.io/github/license/skynet0x01/tugarecon?style=for-the-badge"></a>

                               ______                  ____
                              /_  __/_  ______ _____ _/ __ \___  _________  ____
                               / / / / / / __ `/ __ `/ /_/ / _ \/ ___/ __ \/ __ \
                              / / / /_/ / /_/ / /_/ / _, _/  __/ /__/ /_/ / / / /
                             /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/
                                       /____/    # Coded By skynet0x01 #

*** 18-07-2025 ***
NEWS: New version available 2.3

Tugarecon is a python tool designed to enumerate subdomains using modules. It helps penetration testers and bug hunters collect and gather subdomains for the domain they are targeting.  Bruteforce was integrated was a module to increase the possibility of finding more subdomains using bruteforce with an improved wordlist.
TugaRecon, tribute to Portuguese explorers reminding glorious past of this country.

During the 15th and 16th centuries, Portuguese explorers were at the forefront of European overseas exploration, which led them to reach India, establish multiple trading posts in Asia and Africa, and settle what would become Brazil, creating one of the most powerful empires.

skynet0x01

# Version
NEW *********** 2.3 

More modules will be added!
And much more... :)

# Screenshots

![tugarecon_bughunters](https://user-images.githubusercontent.com/39160972/162957618-02e38cff-942a-4ea5-983b-d3c21eca1f9b.png)

![tugarecon1](https://user-images.githubusercontent.com/39160972/162959038-5fbfc6df-8f18-4c91-b037-0097e6338d9e.png)

Generate network map with ASN clusters and grouped device icons

<img  width="445" height="241" alt="tugarecon" src="https://github.com/user-attachments/assets/2af6193c-fb52-4150-abda-10367033eefa" />

<img width="268" height="236" alt="tugarecon_1" src="https://github.com/user-attachments/assets/0c2c3153-7337-4e00-b916-261f45c030af" />


## Installation

- git clone https://github.com/skynet0x01/tugarecon.git
- pip install -r requirements.txt

────────────────────────────────────────────────────────────

 Available Modules:
 
────────────────────────────────────────────────────────────

  • certspotter     • hackertarget   • ssl           • threatcrowd
  • alienvault      • threatminer    • omnisint      • sublist3r

────────────────────────────────────────────────────────────

 Examples of Usage:
 
────────────────────────────────────────────────────────────

  ▶ Enumerate all modules (except bruteforce):
  
      python3 tugarecon.py -d google.com

  ▶ Use a specific module (e.g., ssl):
  
      python3 tugarecon.py -d google.com --enum ssl

  ▶ Bruteforce subdomains using wordlists:
  
      python3 tugarecon.py -d google.com --bruteforce
      python3 tugarecon.py -d google.com -b

  ▶ View saved results:
  
      python3 tugarecon.py -r

  ▶ Generate network graph (with ASN clusters):
  
      python3 tugarecon.py -d google.com -m


────────────────────────────────────────────────────────────


## Dependencies
You need to install [dnspython](http://www.dnspython.org) to do DNS query

        dnspython>=1.16.0
        argparse
        sys
        time
        datetime
        urllib3
        requests
        webbrowser
        os
        pathlib
        json
        threading
        re 
        queue
        whois
        progress

### DONATIONS:
Donations are welcome. This will help improved features, frequent updates and better overall support.

  - BTC: 18Zg2qiypXRj7QnGWCpcXrKywmcfKkcUSs
  - ETH: 0x177c81746009cd7ab02adf85d28fbf27aca7a240
  - LTC: Le1jfoWqVoEJtm4BYbQRJbggiauMQNqjWy
  - Doge: DSnRY69q1k6xhFkKULSTcSCQdJpVuGeB7k
  - ONE: one1cv90mednznu629p3jr7gqgmqd6qcm368stalwp
  - SOL: 5yRzoxDp17B5XEHSzmgTHWY4NYTWnk7s4qT48t941wyP

   ![tugarecon](https://user-images.githubusercontent.com/39160972/75924110-45d8e300-5e5e-11ea-8832-55c08ecc2902.jpg)
