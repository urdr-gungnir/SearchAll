import requests
import threading
import re

from urllib.parse import urlparse

class BingSpider():
    def __init__(self, page):
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36",
            # "Cookie": "MUID=0D37497B3A146A9009A459B93B2C6B63; _EDGE_V=1; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=BBE8EF5D85544AFFABC19E151D05B49F&dmnchg=1; _SS=SID=14FD12E54B646094309102274AC8612F; MUIDB=0D37497B3A146A9009A459B93B2C6B63; _EDGE_S=SID=14FD12E54B646094309102274AC8612F&mkt=zh-cn&ui=zh-cn; SRCHUSR=DOB=20210930&T=1632976149000&TPC=1632961354000; ipv6=hit=1632979751088&t=4; SNRHOP=I=&TS=; SRCHHPGUSR=SRCHLANG=zh-Hans&BZA=0&BRW=NOTP&BRH=M&CW=724&CH=722&SW=1536&SH=864&DPR=1.25&UTC=480&DM=1&WTS=63768572949&HV=1632976747",
        }
        self.timeout = 5
        self.PAGES = page # 子域名要爬取的页数
        self.KEY_PAGES = 1 # 关键词要爬取的页数
        self.subdomains = []
        self.key_links = []
        self.keywords = ['inurl:admin', 'inurl:login', 'inurl:system', 'inurl:register', 'inurl:upload', 'intitle:后台', 'intitle:系统', 'intitle:登录']
        self.errorurls = []

    def info_processing(self, text):
        return re.findall(r'<h2><a target="_blank" href="(.*?)" h="ID=.*?">(.*?)</a></h2>', text)


    def get_info(self, domain, page ,real_page):
        url = r"https://cn.bing.com/search?q=site:{}&first={}".format(domain, page)
        print('[+]page:第{}页  关键词:[site:{}]  Requesting:[{}] '.format(real_page, domain, url))
        try:
            res = requests.get(url=url, headers=self.header, timeout=self.timeout)
            tmp_subdomains = self.info_processing(res.text)
            for tmp_subdomain in tmp_subdomains:
                self.subdomains += [urlparse(tmp_subdomain[0]).netloc]
        except Exception as e:
            self.subdomains += []
            self.errorurls[url] = e

    def get_key_info(self, domain, keyword='', page=1, real_page=1):
        #https://cn.bing.com/search?q=site%3Atjut.edu.cn+inurl:upload&qs=n&form=QBRE&sp=-1&pq=sitetjut.edu.cn+inurl:upload&sc=1-16&sk=&cvid=6734767D90664B77800EA8092B6BB8DD&first=1
        #https://cn.bing.com/search?q=site%3Abaidu.com&qs=n&form=QBRE&sp=-1&pq=site%3Atjut.edu.cn&sc=1-16&sk=&cvid=6734767D90664B77800EA8092B6BB8DD
        url = r"https://cn.bing.com/search?q=site:{}{}&first={}".format(domain, '+'+keyword, page)
        print('[+]page:第{}页  关键词:[site:{} {}]  Requesting:[{}] '.format(real_page, domain, keyword, url))
        try:
            res = requests.get(url=url, headers=self.header, timeout=self.timeout)
            tmp_key_links = self.info_processing(res.text)
            for tmp_key_link in tmp_key_links:
                self.key_links += [(tmp_key_link[1], tmp_key_link[0])]
                self.subdomains.append(urlparse(tmp_key_link[0]).netloc)
        except Exception as e:
            self.key_links += []
            self.errorurls[url] = e

    def run(self, domain):

        threads = []
        # tmp_page = 1
        # self.get_key_info(domain, self.keyword, tmp_page)
        # self.get_info(domain, tmp_page)
        for keyword in self.keywords:
            for page in range(1, self.KEY_PAGES+1):
                if page == 1:
                    tmp_page = 1
                elif page == 2:
                    tmp_page = 2
                else:
                    tmp_page = (page-2)*10+2
                t = threading.Thread(target=self.get_key_info, args=(domain, keyword, tmp_page, page))
                t.start()
                threads.append(t)
                if(len(threads)>5):
                    for t in threads:
                        t.join()
                    threads = []

        for page in range(1, self.PAGES+1):
            if page == 1:
                tmp_page = 1
            elif page == 2:
                tmp_page = 2
            else:
                tmp_page = (page - 2) * 10 + 2
            t = threading.Thread(target=self.get_info, args=(domain, tmp_page, page))
            t.start()
            threads.append(t)
            if (len(threads) > 5):
                for t in threads:
                    t.join()
                threads = []
        for t in threads:
            t.join()

        if len(self.errorurls) >= 3:
            cprint("[+]There are too many exceptions requested, you need to check.", "red")
            cprint("[+]The exception information is", "red")
            for key in self.errorurls.keys():
                cprint("[+]url:{}\n>>Err:{}".format(key, self.errorurls[key]), "red")

        return list(set(self.subdomains)), list(set(self.key_links))
