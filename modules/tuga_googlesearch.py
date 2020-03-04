# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import go here

import requests
import sys
import re
import time

from bs4 import BeautifulSoup
from urllib.parse import urlparse

from functions import G, W, R
from modules import tuga_useragents
from functions import write_file


class GoogleSearch:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "Google Search"
        self.engine = "googlesearch"
        self.subdomains = set()

        print(G + f"Google: Enumerating subdomains now for {target} \n" + W)
        self.google(target, output)

    ###############################################################################################

    def get_list(self, target, page_number):
        url = f'https://www.google.com/search?q=site:.{target}&ie=utf-8&oe=utf-8&start={page_number}'
        return url

    ###############################################################################################

    def get_url(self, g_clean, page_number):
        if page_number > 30:
            for x in range(len(g_clean)):
                print(g_clean[x])
                time.sleep(0.5)
                if self.output is not None:
                    write_file(g_clean[x], self.engine + '_' + self.output, self.target)


    ###############################################################################################
    def captcha(self):
        for x in range(len(g_clean)):
            print(g_clean[x])
            time.sleep(0.5)
        print(G + "ALERT " + W + "Google systems have detected unusual traffic ")

    ###############################################################################################

    # defining the googleSearch function
    def google(self, target, output):

        # declaring list g_clean to store the fetched urls
        g_clean = []
        page_number = 20

        while page_number < 90:

            # exception handling code to make sure we don't run into errors
            try:
                gurl = self.get_list(target, page_number)
                print(gurl)

                # fetching the response using get method in requests
                html = requests.get(gurl, headers=tuga_useragents.useragent())
                time.sleep(5)

                if page_number > 50:
                    time.sleep(10)

                page_number = page_number + 10

                # checking the response status to be success
                if html.status_code == 429:
                    print(G + "Google systems have detected unusual traffic ", html )
                    print("CAPTCHA detected!!! Maybe try form another IP, or wait..." +W)
                    sys.exit(1)

                if html.status_code == 200:
                    # parsing the fetched html in the response using lxml parser in beautiful soup
                    soup = BeautifulSoup(html.text, 'lxml')

                    # finding all the 'a' tags, links, in the parsed html
                    a = soup.find_all('a')
                    # looping through the all found a tags for processing

                    for i in a:
                        # extracting the href attribute for the link to the search results
                        k = i.get('href')
                        # exception handling code to prevent running into erros

                        try:
                            # search for the pattern of a url to prevent unneccessary attributes in the result using re module
                            m = re.search("(?P<url>https?://[^\s]+)", k)
                            # fetching only the url part in the array
                            n = m.group(0)
                            # splitting the url up to the parameters part to get only the necessary url
                            rul = n.split('&')[0]
                            # print(rul)
                            # parsing the url to divide it into components using urlparse
                            result = urlparse(rul)
                            # print(result)
                            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=result)
                            # checking if the fetched url not belongs to target if true skip the url
                            # print("teste==============  ", domain)
                            if not (re.search(f"{self.target}", domain)):
                                continue
                            # else add it to the result list
                            else:
                                # print("teste==============>  ", domain)
                                url_a = re.compile(r"https?://(www\.)?")
                                url1 = url_a.sub('', domain).strip().strip('/')
                                # print("==============> ", url1)
                                if url1 not in g_clean:
                                    # print("teste: s ", url1)
                                    g_clean.append(url1)
                                else:
                                    continue
                        except:
                            continue
            finally:
                self.get_url(g_clean, page_number)
        if self.output:
            print(f"\nSaving result... {self.engine + '_' + self.output}")
        print(G + "\n[**] TugaRecon is complete." + W)
        print(G + "Please wait some time... before doing a new search with this module\n" + W)