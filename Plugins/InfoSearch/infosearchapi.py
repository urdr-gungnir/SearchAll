'''
InfoSearchApi

:return
type : json
'''
import random

from Common.LogOutput import LogOutput
logger_object = LogOutput()
logger = logger_object.SetModuleName("InfoSearch")
import sys

class InfoSearchApi():
    def __init__(self):
        pass
    def GetSubdomain_ips(self, domain, proxies):
        if domain:
            from Plugins.InfoSearch.Subdomain.subdomainapi import SubdomainApi
            subdomainobject = SubdomainApi(proxies)
            return subdomainobject.Run(domain)
        else:
            logger.error("Need a target domain！")
            sys.exit()

    def GetDomains(self, domain):
        if domain:
            from Plugins.InfoSearch.Domain.domainapi import DomainApi
            domainobject = DomainApi()
            return domainobject.run_domain(domain)
        else:
            logger.error("Need a target domain！")
            sys.exit()

    def get_proxy(self):
        with open("./Common/ProxyPool/DomesticProxyPool.txt", "r") as f:
            proxies = [proxy.strip() for proxy in f.readlines()]
        # current_path = os.path.dirname(__file__)
        # f = open(current_path +"/", "r")
        # proxies = f.readlines()
        return proxies

    def Run(self, domain):
        # proxies = self.get_proxy()
        # proxy = random.choice(proxies)
        Domains, companyname = self.GetDomains(domain)

        for domain in Domains:
            subdomain_ips, key_links = self.GetSubdomain_ips(domain[0])

