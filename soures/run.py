import sys, os
sys.path.append(os.path.abspath(".."))
import pymongo
from soures.digg import main
from soures.config_helper import IniFileHelper
from ky_proxy_helper.ky_proxy_helper import ZiMaProxyHelper
from ky_logging_helper.LogTool import log_tool
from threading import Thread
from soures.aweme_http_client import DouYinEncryptionServerHelper

if __name__ == '__main__':
    config = IniFileHelper('../config.ini')
    client = pymongo.MongoClient(host=["192.168.100.2:27016"])
    data = client[config.get_val('DBClientInfo.database_name')]
    digg_order = data[config.get_val('DiggSetting.order_database_name')]

    # account_database = client['aweme_server'][config.get_val('DiggSetting.account_database_name')]  # 用户表
    account_database = data[config.get_val('DiggSetting.account_database_name')]  # 用户表
    ban_user_info = data[config.get_val('DiggSetting.ban_account_database_name')]  # 被ban的账号
    re_login = data[config.get_val('DiggSetting.re_login_account_database_name')]  # 重新登录表
    re_login_digg1 = data[config.get_val('DiggSetting.re_login1_account_database_name')]  # 重新登录表
    error_data = data[config.get_val('DiggSetting.err_gather_database_name')]  # 记录未出现的点赞失败情况


    #加密接口
    encryption_http_server = DouYinEncryptionServerHelper(config.get_val("EncryptionServer.host"),
                                                          config.get_val("EncryptionServer.port"))

    #本地代理
    proxy_helper = ZiMaProxyHelper(host="192.168.100.2:27016")

    #日志
    log_helper = log_tool()
    log_helper.setlogger('log.txt', True)

    #最小订单数量
    min_order_num = config.get_val('DiggSetting.min_start_order_num', isint=True)

    # 获取线程数量
    thread_num = config.get_val('DiggSetting.thread_num', isint=True)

    trs = []
    # trs.append(Thread(target=socket_server))
    for i in range(thread_num):
        trs.append(Thread(target=main, args=(
            digg_order, account_database, ban_user_info, re_login, error_data, encryption_http_server, proxy_helper,
            log_helper, min_order_num,))
                   )

    for i in trs:
        i.start()

    for i in trs:
        i.join()
    #
    # datas = account_database.find({})
    # for data in datas:
    #     print(data)

