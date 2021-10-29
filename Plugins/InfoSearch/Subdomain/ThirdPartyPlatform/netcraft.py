import time

from Common.LogOutput import LogOutput
logger_object = LogOutput()
logger = logger_object.SetModuleName("netcraft")
import sys
from urllib.parse import urlparse
import requests
import re


# netcraft
class Netcraft():
    def __init__(self):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
        }
        self.subdomains = []
        self.proxy = {"http": "socks5://171.107.184.247:1080/", "https": "socks5://171.107.184.247:1080/"}

    def GetSubdomains(self, url):
        res = requests.get(url, headers=self.header, proxies=self.proxy)
        if "Sorry, no results were found." in res.text:
            return 0
        links = re.findall(r'<a class="results-table__host" href="(.*?)"', res.text)
        for link in links:
            self.subdomains.append(urlparse(link).netloc)
        while "Next Page" in res.text:
            href = re.findall(r'<a class="btn-info" href="(.*?)">Next Page <i class="fas fa-chevron-circle-right"></i></a>', res.text)
            for hr in href:
                url = "https://searchdns.netcraft.com"+hr
                res = requests.get(url, headers=self.header, proxies=self.proxy)
                links = re.findall(r'<a class="results-table__host" href="(.*?)"', res.text)
                for link in links:
                    self.subdomains.append(urlparse(link).netloc)
            time.sleep(0.1)
    def Run(self, domain):
        url = "https://searchdns.netcraft.com/?restriction=site+contains&host={}&position=limited".format(domain)
        self.GetSubdomains(url)
        logger.info("End Netcraft")
        return self.subdomains

# if __name__ == "__main__":
#     a = Netcraft()
#     print(a.Run("tjut.edu.cn"))