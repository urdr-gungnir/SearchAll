#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from Common.LogOutput import LogOutput
logger_object = LogOutput()
logger = logger_object.SetModuleName()
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
except ImportError:
    logger.error('Please use Python > 3.2 to run search_all.')
    sys.exit()



def InfoSearch(domain):
    from Plugins.InfoSearch.infosearchapi import  InfoSearchApi
    infosearchapi = InfoSearchApi()
    infosearchapi.Run(domain)

def GetPorxies():
    from Common import GetProxies
    GetProxies.run_getSocksProxy()


def Banner():
    banner = '''
     ________  _______   ________  ________  ________  ___  ___  ________  ___       ___          
    |\   ____\|\  ___ \ |\   __  \|\   __  \|\   ____\|\  \|\  \|\   __  \|\  \     |\  \         
    \ \  \___|\ \   __/|\ \  \|\  \ \  \|\  \ \  \___|\ \  \\\\\  \ \  \|\  \ \  \    \ \  \        
     \ \_____  \ \  \_|/_\ \   __  \ \   _  _\ \  \    \ \   __  \ \   __  \ \  \    \ \  \       
      \|____|\  \ \  \_|\ \ \  \ \  \ \  \\\\  \\\\ \  \____\ \  \ \  \ \  \ \  \ \  \____\ \  \____  
        ____\_\  \ \_______\ \__\ \__\ \__\\\\ _\\\\ \_______\ \__\ \__\ \__\ \__\ \_______\ \_______\\
       |\_________\|_______|\|__|\|__|\|__|\|__|\|_______|\|__|\|__|\|__|\|__|\|_______|\|_______|
       \|_________|                                                                                   author:Gungnir
    '''
    print('\033[35m' + banner + '\033[0m')


def Init_set():
    Banner()

    global domain, WhetherRunInfoSearch, WhetherGetProxies

    import argparse

    parser = argparse.ArgumentParser(description='''
    (￢︿̫̿￢☆)，哼，可恶! 竟然发现我了.
     (ˉ▽￣～)   既然发现我了，那就给你吧！
    ''')
    parser.add_argument("-d", "--domain", help="Need a target domain", dest="domain")
    parser.add_argument("-i", "--InfoSearch", help="Conduct information collection", dest="WhetherRunInfoSearch", action="store_true")
    parser.add_argument("-p", "--Proxy", help="Get proxies", dest="WhetherGetProxies", action="store_true")

    args = parser.parse_args()
    options = vars(args)


    domain, WhetherRunInfoSearch, WhetherGetProxies = options['domain'], options['WhetherRunInfoSearch'], options['WhetherGetProxies']

    # GetProxies
    if(WhetherGetProxies):
        GetPorxies()


    # 判断用户要不要信息收集
    if(WhetherRunInfoSearch):
        # GetSubdomains(domain)
        InfoSearch(domain)
    # else:
    #     logger.error('At least one run command parameter is required, please use the --help or -h command for details')
    #     sys.exit()

if __name__ == '__main__':



    '''初始化参数'''
    Init_set()
