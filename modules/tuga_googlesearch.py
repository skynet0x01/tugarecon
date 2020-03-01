# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import go here

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

from functions import G, W
from modules import tuga_useragents
from functions import write_file


class GoogleSearch:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "Google Search"
        self.engine = "googlesearch"
        self.query = 100
        self.subdomains = set()
        self.page_number =1

        print(G + f"Google: Enumerating subdomains now for {target} \n" + W)
        url = self.subdomains_list()
        self.sub = self.google(url)
        self.enumerate()

    def enumerate(self):
        for x in range(len(self.sub)):
            print (self.sub[x])

            # making the url ready for requests
    def subdomains_list(self):
        url = f'https://www.google.com/search?client=ubuntu&channel=fs&q=site:{self.target}&ie=utf-8&oe=utf-8&start={self.page_number}'.format(self.query)
        # https://www.google.com/search?q=site:sapo.pt&client=ubuntu&hs=Zmv&channel=fs&ei=lgtbXoa4CsXggweUp4H4Dg&start=10&sa=N&ved=2ahUKEwiG27Dsi_jnAhVF8OAKHZRTAO8Q8tMDegQICxA3&biw=1472&bih=682
        return url

    # defining the googleSearch function
    def google(self, url):
        # declaring list g_clean to store the fetched urls
        g_clean = []
        # exception handling code to make sure we don't run into errors
        try:
            # fetching the response using get method in requests
            html = requests.get(url, headers=tuga_useragents.useragent())
            # checking the response status to be success
            if html.status_code == 200:
                # parsing the fetched html in the response using lxml parser in beautiful soup
                soup = BeautifulSoup(html.text, 'lxml')
                if html.text.find("Our systems have detected unusual traffic") != -1:
                    print("CAPTCHA detected - Plata or captcha !!!Maybe try form another IP...")
                    return True
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
                        #print(rul)
                        # parsing the url to divide it into components using urlparse
                        domain = urlparse(rul)
                        #print(domain)
                        # checking if the fetched url belongs to google.com if true skip the url
                        if not (re.search(f"{self.target}", domain.netloc)):
                            continue
                        # else add it to the result list
                        else:
                            g_clean.append(rul)
                            # print("t: ")
                            # print("teste: ", g_clean)
                    except:
                        continue
        except Exception as ex:
            print(str(ex))
        # finally return the result urls
        finally:
            return g_clean
