from Common.LogOutput import LogOutput
logger_object = LogOutput()
logger = logger_object.SetModuleName("GetProxies")

import sys

import requests
import base64
import json
import configparser
from threading import Thread
from queue import Queue
import random
import urllib3
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cf = configparser.ConfigParser()
cf.read("./config.ini")
secs = cf.sections()
email = cf.get('fofa api', 'EMAIL')
key = cf.get('fofa api', 'KEY')

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Connection': 'close'}

size = 10000
page = 1
today = datetime.date.today()
oneday = datetime.timedelta(days=1)
yesterday = today - oneday


# 访问百度和谷歌

def curlWeb(socks5_proxys_queue, socksProxysDict):
    while not socks5_proxys_queue.empty():
        proxy = socks5_proxys_queue.get()
        requests_proxies = {"http": "socks5://{}".format(proxy), "https": "socks5://{}".format(proxy)}
        baidu_url = "https://www.baidu.com"
        google_url = "https://www.google.com"

        try:
            res2 = requests.get(url=google_url, headers=headers, timeout=10, verify=False, proxies=requests_proxies)
            if res2.status_code == 200:
                logger.info("{} 成功访问谷歌 [{}]".format(proxy, res2.status_code))
                socksProxysDict["google"].append(proxy)
                continue
        except Exception as e:
            pass

        try:
            res = requests.get(url=baidu_url, headers=headers, timeout=10, verify=False, proxies=requests_proxies)
            if res.status_code == 200:
                logger.info("{} 成功访问百度 [{}]".format(proxy, res.status_code))
                socksProxysDict["baidu"].append(proxy)
        except Exception as e:
            pass


def query_socks5(yesterday):
    query_str = r'protocol=="socks5" && "Version:5 Method:No Authentication(0x00)" && after="{}" && country="CN"'.format(yesterday)
    qbase64 = str(base64.b64encode(query_str.encode(encoding='utf-8')), 'utf-8')
    url = r'https://fofa.so/api/v1/search/all?email={}&key={}&qbase64={}&size={}&page={}&fields=host,title,ip,domain,port,country,city,server,protocol'.format(email, key, qbase64, size, page)
    print(url)
    socks5_proxys = []
    try:
        ret = json.loads(requests.get(url=url, headers=headers, timeout=10, verify=False).text)
        fofa_Results = ret['results']
        for result in fofa_Results:
            host, title, ip, domain, port, country, city, server, protocol = result
            proxy = ip + ":" + port
            socks5_proxys.append(proxy)
    except Exception as e:
        logger.error('fofa inquire {} : {}'.format(query_str, e.args))
    return socks5_proxys

def SaveToProxyPool(baidu_proxies, google_proxies):
    try:
        with open("./Common/ProxyPool/DomesticProxyPool.txt", "a") as f:
            for baidu_proxy in baidu_proxies:
                f.write(baidu_proxy+'\n')
        logger.info("The domestic proxies is stored in the file path as Common/ProxyPool/DomesticProxyPool.txt")
        with open("./Common/ProxyPool/ForeignProxyPool.txt", "a") as f:
            for google_proxy in google_proxies:
                f.write(google_proxy+'\n')
        logger.info("The foreign proxies is stored in the file path as Common/ProxyPool/ForeignProxyPool.txt")
    except:
        logger.error("Error opening file")
        sys.exit()
def run_getSocksProxy():
    logger.info("Start Searching Proxies")
    socksProxysDict = {"baidu": [], "google": []}
    socks5_proxys = query_socks5(yesterday)
    socks5_proxys_queue = Queue(-1)
    if socks5_proxys:
        # 随机取1000个代理ip
        for eachSocks5 in random.sample(socks5_proxys, 50):
            socks5_proxys_queue.put(eachSocks5)

        threads = []
        for num in range(100):
            t = Thread(target=curlWeb, args=(socks5_proxys_queue, socksProxysDict))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    baidu_proxies = socksProxysDict.get('baidu')
    google_proxies = socksProxysDict.get('google')
    SaveToProxyPool(baidu_proxies, google_proxies)
    logger.info("Find {} DomesticProxies and {} ForeignProxies".format(len(baidu_proxies), len(google_proxies)))
    logger.info("End Searching Proxies")
    # return baidu_proxies, google_proxies


