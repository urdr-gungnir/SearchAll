'''
得到subdomain的api
'''
import sys
import requests

from Common.LogOutput import LogOutput

logger_object = LogOutput()
logger = logger_object.SetModuleName("subdomains")

class SubdomainApi():

    def __init__(self):
        self.global_subdomains = []
        self.global_subdomains_ips = []
        self.global_key_links = []
        self.links = []
        self.global_CDNSubdomainsDict = []
        # self.proxies = proxies

    def WebSpiderSubdomains(self, domain):
        # proxies = self.proxies
        def BaiduSpider(domain):
            logger.info('Start Baidu Spider')

            from Plugins.InfoSearch.Subdomain.Spider.Baidu.baidu import BaiduSpider
            BaiduSpider = BaiduSpider()
            tmp_subdomains, tmp_key_links, tmp_links = BaiduSpider.run(domain)
            self.global_subdomains += tmp_subdomains
            self.global_key_links += tmp_key_links
            self.links += tmp_links
            logger.info('Baidu Spider Is Over')

        # bing的请求一直有问题
        def BingSpider(domain):
            logger.info('Start Bing Spider')

            from Plugins.InfoSearch.Subdomain.Spider.Bing.bing import BingSpider
            BingSpider = BingSpider()
            tmp_subdomains, tmp_key_links, tmp_links = BingSpider.run(domain)

            self.global_subdomains += tmp_subdomains
            self.global_key_links += tmp_key_links
            self.links += self.links
            logger.info('Bing Spider Is Over')


        logger.info("Start Spider Module")
        BaiduSpider(domain)
        # BingSpider(domain, proxies)
        logger.info("WebSpider is over")

    def ThirdPartyPlatform(self, domain):
        # proxies = self.proxies
        # proxy = random.choice(proxies)
        def Certificate(domain):

            from Plugins.InfoSearch.Subdomain.ThirdPartyPlatform.certificate import Certificate
            Certificate = Certificate()
            tmp_subdomains = Certificate.run(domain)

            self.global_subdomains += tmp_subdomains

        def Netcraft(domain):
            from Plugins.InfoSearch.Subdomain.ThirdPartyPlatform.netcraft import Netcraft
            Netcraft = Netcraft()
            tmp_subdomains = Netcraft.Run(domain)

            self.global_subdomains += tmp_subdomains
        logger.info("ThirdPartyPlatform start")
        Certificate(domain)
        Netcraft(domain)
        logger.info("ThirdPartyPlatform end")


    '''DNS解析'''
    def Dns_resolver(self):
        import dns.resolver
        dns_servers = [
            # DNS对结果准确性影响非常大，部分DNS结果会和其它DNS结果不一致甚至没结果
            # '223.5.5.5',  # AliDNS
            # '114.114.114.114',  # 114DNS
            # '1.1.1.1',  # Cloudflare
            '119.29.29.29',  # DNSPod https://www.dnspod.cn/products/public.dns
            # '180.76.76.76',  # BaiduDNS
            # '1.2.4.8',  # sDNS
            # '11.1.1.1'  # test DNS, not available
            # '8.8.8.8', # Google DNS, 延时太高了
        ]

        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = dns_servers

        def DNS_Query(domain_name, domain_type):
            try:
                ips = ''
                A = my_resolver.resolve(domain_name, domain_type)
                for ip in A.rrset.items.keys():
                    ips = ips + str(ip) + ','
                return ips.strip(",")
            except Exception as e:
                return 'null'


        logger.info("Dns_resolver start")
        for single_subdomain in self.global_subdomains:
            ips = DNS_Query(single_subdomain, "A")
            self.global_subdomains_ips += [(single_subdomain, ips)]

        logger.info("Dns_resolver end")


    def ESD_Run(self, domain):
        logger.info("ESD start")
        from Plugins.InfoSearch.Subdomain.ESD.ESD import EnumSubDomain
        self.global_subdomains_ips += EnumSubDomain(domain).run()
        logger.info("ESD end")

    def Check_network_connectivity(self):
        try:
            logger.info("Checking the network")
            if requests.get("https://www.baidu.com").status_code == 200:
                logger.info("Network status is good")
        except:
            logger.error("You need to check the network settings.Network problems")
            sys.exit()
    def JsFinderRun(self):
        from Plugins.InfoSearch.Subdomain.JsFinder import jsfinder
        for link in self.links:
            self.global_subdomains += jsfinder.RunJsFinder(link)


    # def Save_Subdomains(self, domain):
    #     f = open('../../../Reports/{}-{}-{}-{}'.format(domain, datetime.datetime.now().year, datetime.datetime.now().month,datetime.datetime.now().day), 'w')
    #     print(list(set(self.global_subdomains_ips)))
    #
    #     print("The subdomain is stored in Reports/{}".format(f.name))
    #
    #     for i in self.global_subdomains_ips:
    #         f.write(i[0] + '      ' + i[1] + '\n')
    #     f.close()
    #     logger.error("There is something wrong in network")


    def Data_Filtering(self, domain):
        logger.info("Data filtering start")
        if ('') in self.global_subdomains:
            self.global_subdomains.remove('')
        if (domain) in self.global_subdomains:
            self.global_subdomains.remove(domain)
        self.global_subdomains = list(set(self.global_subdomains))
        logger.info("Data filtering end")


    def CheckCDN(self):
        from Plugins.InfoSearch.Subdomain.IsCND import CheckCDN
        self.subdomain_ips ,self.global_CDNSubdomainsDict = CheckCDN.run_checkCDN(self.global_subdomains)

    def Run(self, domain):
        logger.info("Subdomains start")



        # self.Check_network_connectivity()

        self.WebSpiderSubdomains(domain)
        self.JsFinderRun()
        self.ThirdPartyPlatform(domain)


        self.Data_Filtering(domain)
        self.CheckCDN()

        # self.Dns_resolver()

        # self.ESD_Run(domain)

        logger.info("Subdomains end")
        return list(set(self.global_subdomains_ips)), self.global_key_links

