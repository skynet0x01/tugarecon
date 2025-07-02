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

*** 02-06-2025 ***
NEWS: New version available 2.0

Tugarecon is a python tool designed to enumerate subdomains using modules. It helps penetration testers and bug hunters collect and gather subdomains for the domain they are targeting.  Bruteforce was integrated was a module to increase the possibility of finding more subdomains using bruteforce with an improved wordlist.
TugaRecon, tribute to Portuguese explorers reminding glorious past of this country.

During the 15th and 16th centuries, Portuguese explorers were at the forefront of European overseas exploration, which led them to reach India, establish multiple trading posts in Asia and Africa, and settle what would become Brazil, creating one of the most powerful empires.

skynet0x01

# Version
NEW *********** 2.0 

More modules will be added!
And much more... :)

# Screenshots

![tugarecon_bughunters](https://user-images.githubusercontent.com/39160972/162957618-02e38cff-942a-4ea5-983b-d3c21eca1f9b.png)

![tugarecon1](https://user-images.githubusercontent.com/39160972/162959038-5fbfc6df-8f18-4c91-b037-0097e6338d9e.png)


## Installation

- git clone https://github.com/skynet0x01/tugarecon.git
- pip install -r requirements.txt

## Usage

        python3 tugarecon.py -d google.com
        python3 tugarecon.py -d google.com --savemap
        python3 tugarecon.py -d google.com --bruteforce
        python3 tugarecon.py -d google.com --bruteforce --full
        python3 tugarecon.py -d google.com -b --full
        python3 tugarecon.py -r

## Modules

    bruteforce (tuga_bruteforce - wildcards, wordlist)
    certspotter
    ssl
    hackertarget
    threatcrowd
    Alienvault
    Threatminer
    Omnisint
    API Sublist3r

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

  - BTC: 17EbiXrVAvAqgkyunPYPBdKKz2AFHmb7mZ
  - ETH: 0x642187e3f8F9CaF95d92df823D17E8020c50647E
  - LTC: LLsJVJibVFRqYjnxbUfhYFd4kSowcRHdcN
  - Doge: DPWbTMEaqTNzpfC5oYC1xcScT9dQBW17MW
  - ONE: one1q2y2hntw32yakh6fxk5ls7dkvswfuhcm70ymvh
  - SCRT: secret1fc88f5asq3lmkrhst2shsa7ew5fxt7qapjsda7

   ![tugarecon](https://user-images.githubusercontent.com/39160972/75924110-45d8e300-5e5e-11ea-8832-55c08ecc2902.jpg)
