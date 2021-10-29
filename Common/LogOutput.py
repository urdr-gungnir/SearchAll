'''
log output

a = LogOutput()
Logger_object = a.SetModuleName("Module_name")
Looger_object.wrong("log_info") / Looger_object.error("log_info") / Looger_object.info("log_info")
'''

import colorlog
import logging


class LogOutput():
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        self.mycolorlog = colorlog
        self.handler = self.mycolorlog.StreamHandler()
        formatter = self.mycolorlog.ColoredFormatter(
            '%(log_color)s[+] %(asctime)s [%(name)s] [%(levelname)s] %(message)s%(reset)s',
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'white,bg_red',
                'Module': 'purple'
            },
            secondary_log_colors={},
            style='%'
        )
        self.handler.setFormatter(formatter)


    def SetModuleName(self, module_name=''):
        if module_name == '':
            self.logger = self.mycolorlog.getLogger('Seach_all')
        else:
            self.logger = self.mycolorlog.getLogger('Seach_all  {}'.format(module_name))
        self.logger.addHandler(self.handler)
        self.logger.setLevel(self.mycolorlog.INFO)
        return self.logger