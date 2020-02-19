# TugaRecon
  tugarecon is a python tool designed to enumerate subdomains using modules. It helps penetration testers and bug hunters collect and gather subdomains for the domain they are targeting.  Bruteforce was integrated was a module to increase the possibility of finding more subdomains using bruteforce with an improved wordlist.
TugaRecon, tribute to Portuguese explorers reminding glorious past of this country.

During the 15th and 16th centuries, Portuguese explorers were at the forefront of European overseas exploration, which led them to reach India, establish multiple trading posts in Asia and Africa, and settle what would become Brazil, creating one of the most powerful empires.

# Version
0.30 beta


During the development phase, we would like to invite all of you, to help test the beta version of the application.

More modules will be added!
New features!
And much more... :)

# Screenshots

![Screenshot from 2020-02-06 19-29-27](https://user-images.githubusercontent.com/39160972/73971658-2f02a780-4917-11ea-9c5f-ad37c43facb6.png)

![tugarecon1](https://user-images.githubusercontent.com/39160972/72821211-1da77300-3c68-11ea-80a9-db8ea6716e4b.png)

![Screenshot from 2020-01-26 20-59-16](https://user-images.githubusercontent.com/39160972/73141832-4d97b180-4080-11ea-9adc-a83667ea9687.png)

# Installation

git clone https://github.com/LordNeoStark/tugarecon.git

# Usage

        python3 tugarecon.py -d google.com
        python3 tugarecon.py -d google.com --enum ssl
        python3 tugarecon.py -d google.com --enum certspotter --savemap
        python3 tugarecon.py -d google.com -o google.txt
        python3 tugarecon.py -d google.com --savemap
        python3 tugarecon.py -d google.com --bruteforce

# Dependencies
You need to install [dnspython](http://www.dnspython.org) to do DNS query

        pip install dnspython

# DONATIONS:

Donations are welcome. This will help improved features, frequent updates and better overall support.

BTC:   1C1q8c2bpSvRBpupD43p1CAV98YXkNnnDx

Doge:  DRU62QbterkCpMHEG7ZMSZXEJQzyR13CRB

# News
- [x] Fast enumerate BruteForce scan upgrade
- [x] Mapping the domain and save image results/target.png
- [x] add new module
- [x] add new folder /results
