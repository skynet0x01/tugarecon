# TugaRecon - funcions, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
import sys
import urllib.request
import webbrowser
import urllib.error
import urllib3
import os
import datetime
from pathlib import Path
################################################################################
# Colors
global G, Y, B, R, W

G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'  # white
################################################################################
def write_file(subdomains, target):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()

    # saving subdomains results to output file
    folder = os.path.join(pwd, "results/" + target + "/" + date)
    try:
        os.makedirs(folder)
    except:
        pass
    try:
        with open("results/" + target + "/" + "tmp.txt", 'a') as tmp:
            tmp.write(subdomains + '\n')
        tmp.close()
    except:
        pass
################################################################################
def DeleteDuplicate(target):
    date = str(datetime.datetime.now().date())
    content = open("results/" + target + "/" + "tmp.txt", 'r').readlines()
    content_set = set(content)
    cleandata = open("results/" + target + "/" + date + "/" + "subdomains.txt", 'w')
    for line in content_set:
        cleandata.write(line)
    try:
        os.remove("results/"+ target + "/" + "tmp.txt")
    except OSError:
        pass
################################################################################
def ReadFile(target):
    date = str(datetime.datetime.now().date())
    pwd = os.getcwd()
    folder = os.path.join(pwd, "results/" + target + "/" + date)

    file = open("results/" + target + "/" + date + "/" + "subdomains.txt", 'r')
    lines = file.readlines()

    for index, line in enumerate(lines):
        print("     [*] {}:  {}".format(index, line.strip()))
    file.close()
    print("\n[*] Total Subdomains Found: {}".format(index))
    print(Y + "\n\n[+] Output Result" + W)
    print(G + "**************************************************************" + W)
    print(R + "         ->->-> " + W, folder + "\n")
################################################################################
def mapping_domain(target):
    date = str(datetime.datetime.now().date())
    if not os.path.exists("results/" + target + "/" + date):
        os.mkdir("results/" + target + "/" + date)
    else:
        pass
    try:
        try:
            urllib.request.urlretrieve(f"https://dnsdumpster.com/static/map/{target}" + ".png",
                                       f"results/{target}/"+ date + f"/{target}.png")
        except urllib.error.URLError as e:
            print("", e.reason)
        my_file = Path(f"results/{target}/"+ date + f"/{target}.png")
        if my_file.is_file():
            webbrowser.open(f"results/{target}/"+ date + f"/{target}.png")
        else:
            print(Y + "\nOops! The map file was not generated. Try again...\n" + W)
    except PermissionError:
        print("You dont have permission to save a file, use sudo su")
