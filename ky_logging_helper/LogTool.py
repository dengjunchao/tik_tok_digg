# -*- coding: utf-8 -*-
import sys,os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Singleton import singleton_ex
import logging
import time



class log_tool(object):
    __metaclass__ = singleton_ex

    def __init__(self):
        super(log_tool, self).__init__()
        self.logger = None

    def setlogger(self, name, show=False):
        if self.logger is None:
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level=logging.DEBUG)
            self.__setfile(name)
            if show is True:
                self.__setconsole()

    def __setfile(self, name):
        try:
            if not os.path.exists("./log/"):
                os.makedirs("./log/")
        except:
            pass
        logName = "./log/%s-%s.log" % (name,
                                       time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time())))
        self.handler = logging.FileHandler(logName)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d] %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)

    def __setconsole(self):
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d] %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S")
        controlHandle = logging.StreamHandler()
        controlHandle.setLevel(logging.DEBUG)
        controlHandle.setFormatter(formatter)
        self.logger.addHandler(controlHandle)
