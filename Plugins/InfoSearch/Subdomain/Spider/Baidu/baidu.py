
import random

import requests
import threading
import re
from urllib.parse import urlparse
from Common.LogOutput import LogOutput
logger_object = LogOutput()
logger = logger_object.SetModuleName("BaiduSpider")

class MyThread(threading.Thread):
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args
    def run(self):
        self.result = self.func(*self.args)
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None
class BaiduSpider():
    def __init__(self, proxies):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            # "Cookie": "MUID=0D37497B3A146A9009A459B93B2C6B63; _EDGE_V=1; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=BBE8EF5D85544AFFABC19E151D05B49F&dmnchg=1; _SS=SID=14FD12E54B646094309102274AC8612F; MUIDB=0D37497B3A146A9009A459B93B2C6B63; _EDGE_S=SID=14FD12E54B646094309102274AC8612F&mkt=zh-cn&ui=zh-cn; SRCHUSR=DOB=20210930&T=1632976149000&TPC=1632961354000; ipv6=hit=1632979751088&t=4; SNRHOP=I=&TS=; SRCHHPGUSR=SRCHLANG=zh-Hans&BZA=0&BRW=NOTP&BRH=M&CW=724&CH=722&SW=1536&SH=864&DPR=1.25&UTC=480&DM=1&WTS=63768572949&HV=1632976747",
        }
        self.timeout = 5
        self.PAGES = 10000 # 子域名要爬取的页数
        self.KEY_PAGES = 2 # 关键词要爬取的页数
        self.subdomains = []
        self.key_links = []
        self.links = []
        self.keywords = ['inurl:admin', 'inurl:login', 'inurl:system', 'inurl:register', 'inurl:upload', 'intitle:后台', 'intitle:系统', 'intitle:登录']
        self.errorurls = {} # 存放第一次报异常的url，和异常原因， 3秒后重新进行请求。
        self.proxies = proxies

    def info_processing(self, text):
        return re.findall(r'<div class="c-tools c-gap-left" id="\S*" data-tools=\'{"title":"(.*)","url":"(.*)"}\'>', text)



    def real_url(self, link):
        try:
            real_link = requests.get(link, allow_redirects=False, timeout=self.timeout).headers.get('Location')
            return real_link
        except:
            return link

    def get_proxy(self):
        return random.choice(self.proxies)


    def get_info(self, domain, page=0):
        url = r"https://www.baidu.com/s?wd=site:{}&pn={}0".format(domain, page)
        print('[+]page:第{}页  关键词:[site:{}]  Requesting:[{}] '.format(page+1, domain, url))
        # proxies = {
        #     "http": "socks5://{}".format(proxy),
        #     "https": "socks5://{}".format(proxy)
        # }
        try:
            res = requests.get(url=url, headers=self.header, timeout=self.timeout)
            if self.check_page(res.text, page+1) == 'Stop':
                return 'Stop'
            tmp_subdomains = self.info_processing(res.text)
            for tmp_subdomain in tmp_subdomains:
                tmp_real_link = self.real_url(tmp_subdomain[1])
                self.subdomains += [urlparse(tmp_real_link).netloc]
                self.links.append(tmp_real_link)
                logger.info(urlparse(tmp_real_link).netloc)
        except Exception as e:
            self.subdomains += []
            self.errorurls[url] = e



    def get_key_info(self, domain, keyword='', page=0):
        url = r"https://www.baidu.com/s?wd=site:{}{}&pn={}0".format(domain, '+'+keyword, page)
        print('[+]page:第{}页  关键词:[site:{} {}]  Requesting:[{}] '.format(page+1, domain, keyword, url))
        # proxies = {
        #     "http": "socks5://{}".format(proxy),
        #     "https": "socks5://{}".format(proxy)
        # }
        try:
            res = requests.get(url=url, headers=self.header, timeout=self.timeout)
            tmp_key_links = self.info_processing(res.text)
            for tmp_key_link in tmp_key_links:
                tmp_real_link = self.real_url(tmp_key_link[1])
                self.key_links += [(tmp_key_link[0], tmp_real_link)]
                self.subdomains.append(urlparse(tmp_key_link[0]).netloc)
                logger.info(urlparse(tmp_real_link).netloc)
        except Exception as e:
            self.key_links += []
            self.errorurls[url] = e


    def check_page(self, text, page):
        num = re.findall(r'<strong><span class="page-item_M4MDr pc">(\d*?)</span></strong>', text)
        if (num != ['{}'.format(page)]) and (page != 1):
            return 'Stop'
        else:
            print("{}页没问题， num = {}".format(page, num))
            return 'Contiune'


    '''
        返回一个子域名列表和一个包含title和连接的link列表
    '''
    def run(self, domain):
        threads = []
        num = 1
        flag = 1
        try:
            while flag != 0:
                # proxy = self.get_proxy()
                for page in range(0+(num-1)*5, 5+(num-1)*5):
                    # t = MyThread(self.get_info, args=(domain, proxy, page))
                    t = MyThread(self.get_info, args=(domain, page))
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
                    if(t.get_result() == 'Stop'):
                        flag = 0
                num += 1


            for keyword in self.keywords:
                # proxy = self.get_proxy()
                for page in range(0, self.KEY_PAGES):
                    t = threading.Thread(target=self.get_key_info, args=(domain, keyword, page))
                    # t = threading.Thread(target=self.get_key_info, args=(domain, proxy, keyword, page))
                    t.start()
                    threads.append(t)
            for t in threads:
                t.join()

        #     if len(self.errorurls)>=3:
        #         cprint("[+]There are too many exceptions requested, you need to check.", "red")
        #         cprint("[+]The exception information is", "red")
        #         for key in self.errorurls.keys():
        #             cprint("[+]url:{}\n>>Err:{}".format(key, self.errorurls[key]), "red")
        except:
            return list(set(self.subdomains)), list(set(self.key_links)), list(set(self.links))
        # # print(set(self.subdomains)), list(set(self.key_links))
        return list(set(self.subdomains)), list(set(self.key_links)), list(set(self.links))