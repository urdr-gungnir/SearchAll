import requests
import re
from urllib.parse import quote
import json
import math

from Common.LogOutput import LogOutput
logger_object = LogOutput()

logger = logger_object.SetModuleName('Domain')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0'}

class DomainApi():
    def __init__(self):
        # self.proxy = {"http": "http://{}".format(proxy), "https": "https://{}".format(proxy)}
        pass
    def chinazApi(self, domain):
        # 解析chinaz返回结果的json数据
        def parse_json(json_ret):
            chinazNewDomains = []
            results = json_ret['data']
            for result in results:
                companyName = result['webName']
                newDomain = result['host']
                time = result['verifyTime']
                chinazNewDomains.append((companyName, newDomain, time))
            chinazNewDomains = list(set(chinazNewDomains))
            return chinazNewDomains


        chinazNewDomains = []
        tempDict = {}
        tempList = []

        # 获取域名的公司名字
        url = r'http://icp.chinaz.com/{}'.format(domain)
        try:
            res = requests.get(url=url, headers=headers, allow_redirects=False, verify=False, timeout=10)
        except Exception as e:
            logger.error(url+' '+e.args)
            return [], []
        text = res.text

        companyName = re.search("var kw = '([\S]*)'", text)
        if companyName:
            companyName = companyName.group(1)
            logger.info('公司名: {}'.format(companyName))
            companyNameUrlEncode = quote(str(companyName))
        else:
            logger.warning('没有匹配到公司名')
            return [], []

        # 备案反查域名
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        url = 'http://icp.chinaz.com/Home/PageData'
        data = 'pageNo=1&pageSize=20&Kw=' + companyNameUrlEncode
        try:
            res = requests.post(url=url, headers=headers, data=data, allow_redirects=False, verify=False, timeout=10)
        except Exception as e:
            logger.error('{} {}'.format(url, e.args))
            return [], []

        json_ret = json.loads(res.text)
        if 'amount' not in json_ret.keys():
            return chinazNewDomains, []
        amount = json_ret['amount']
        pages = math.ceil(amount / 20)
        logger.info('页数: {}'.format(pages))
        tempList.extend(parse_json(json_ret))

        # 继续获取后面页数
        for page in range(2, pages+1):
            logger.info('请求第{}页'.format(page))
            data = 'pageNo={}&pageSize=20&Kw='.format(page) + companyNameUrlEncode
            try:
                res = requests.post(url=url, headers=headers, data=data, allow_redirects=False, verify=False, timeout=10)
                json_ret = json.loads(res.text)
                tempList.extend(parse_json(json_ret))
            except Exception as e:
                logger.error('{} {}'.format(url, e.args))

        for each in tempList:
            if each[1] not in tempDict:
                tempDict[each[1]] = each
                chinazNewDomains.append(each)

        return chinazNewDomains, companyName

    def run_domain(self, domain):
        beianNewDomains = []
        chinazNewDomains, companyName = self.chinazApi(domain)

        tempDict = {}
        for each in chinazNewDomains:
            if each[1] not in tempDict:
                tempDict[each[1]] = each
                beianNewDomains.append(each)

        logger.info("去重后共计{}个顶级域名".format(len(beianNewDomains)))
        print("\033[33m"+"The top-level domain name is shown below"+"\033[0m")

        for _ in beianNewDomains:
            print(_)

        p = re.compile("[^0-9a-zA-Z.]+")
        judge = 'y'
        for _ in beianNewDomains:
            if p.match(_[1]):
                logger.critical("I’m not sure if [{}] is a top-level domain name, you need to judge. (y/n)".format(_[1]))
                judge = input()
                while(judge != 'y' and judge !='n'):
                    logger.critical("I’m not sure if [{}] is a top-level domain name, you need to judge. (y/n)".format(_[1]))
                    judge = input()
                if(judge == 'y'):
                    continue
                else:
                    beianNewDomains.remove(_)
            else:
                continue
        logger.info("A total of {} top-level domain name after screening".format(len(beianNewDomains)))
        for _ in beianNewDomains:
            print(_[1])

        return beianNewDomains, companyName
# [('同济大学浙江学院', 'tjzj.edu.cn', '2021-01-14')]   同济大学浙江学院