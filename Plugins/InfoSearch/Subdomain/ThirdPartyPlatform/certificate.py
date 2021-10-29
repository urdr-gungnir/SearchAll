from Common.LogOutput import LogOutput
logger_object = LogOutput()
logger = logger_object.SetModuleName("certificate")
import sys

import requests
import re

# crt.sh
class Certificate():
    def __init__(self):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
        }
        self.subdomains = []

    # def Get_subdomain(self):

    def run(self, domain):
        try:
            res = requests.get("https://crt.sh/?q={}".format(domain), headers=self.header)
            before_subdomains = re.findall(r"<TD>(.*.{})*?</TD>".format(domain), res.text)
            before_subdomains = list(set(before_subdomains))
            for subdomains in before_subdomains:
                if '<BR>' in subdomains:
                    subdomain_list = subdomains.split("<BR>")
                    for subdomain in subdomain_list:
                        if '*' in subdomain or '@' in subdomain:
                            continue
                        self.subdomains.append(subdomain)
                    continue
                if '*' in subdomains or '@' in subdomains:
                    continue
                self.subdomains.append(subdomains)
        except:
            logger.error("There are too many exceptions requested, you need to check.")
            sys.exit()
        return list(set(self.subdomains))

# 测试成功
# a = Certificate()
# print(a.run('tjut.edu.cn'))