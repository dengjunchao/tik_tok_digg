"""点赞服务_LaoSi"""
# import re
import base64
import json
import random
import datetime
import time
import uuid
from time import time, mktime, strptime, sleep
from urllib.parse import quote
from bson import ObjectId
from libs.json_encoder import JSONEncoder

import requests
from requests.exceptions import ProxyError, Timeout, ConnectionError, ConnectTimeout
from ky_proxy_helper import ZiMaProxyHelper, KaYuException
from soures.aweme_http_client import DouYinEncryptionServerHelper
import socket
##########################
import pymongo
from soures.config_helper import IniFileHelper
from ky_logging_helper.LogTool import log_tool
from config import TIKTOK_HOST, TIKTOK_FAILED_ORDERS

##########################


requests.packages.urllib3.disable_warnings()

# 全部变量 线程共用 无安全
socket_cmd = "start"


def get_account(account_database) -> dict:
    """
    用于获取不在点赞工作状态或冷却的账号
    :param account_database: 机器人账号数据库对象
    :return:None or ditc
    """

    # 优先获取冷却完成后代理还未过期的账号

    account_info = account_database.find_one_and_update(
        {'$and': [
            {'digg_status': 0},
            {'digg_cold_time': {'$lt': int(time())}
             }, {'expire_time': {'$gt': int(time())}
                 }
        ]},
        {"$set": {"digg_status": 0}}, {"user_id": 1,
                                       "is_digg_item_id": 1,
                                       "expire_time": 1,
                                       "iid": 1,
                                       "did": 1,
                                       "sid_guard": 1,
                                       "ttreq": 1,
                                       "openudid": 1,
                                       "odin_tt": 1,
                                       "uid_tt": 1,
                                       "sid_tt": 1,
                                       "session_key": 1,
                                       "device_brand": 1,
                                       "device_type": 1,
                                       "version_code": 1,
                                       "os_version": 1,
                                       "proxies": 1
                                       })

    if not account_info:
        account_info = account_database.find_one_and_update(
            {'$and': [
                {'digg_status': 0},
                {'digg_cold_time': {'$lt': int(time())}
                 }
            ]},
            {"$set": {"digg_status": 1}}, {"user_id": 1,
                                           "is_digg_item_id": 1,
                                           "expire_time": 1,
                                           "iid": 1,
                                           "did": 1,
                                           "sid_guard": 1,
                                           "ttreq": 1,
                                           "openudid": 1,
                                           "odin_tt": 1,
                                           "uid_tt": 1,
                                           "sid_tt": 1,
                                           "session_key": 1,
                                           "device_brand": 1,
                                           "device_type": 1,
                                           "version_code": 1,
                                           "os_version": 1,
                                           "proxies": 1
                                           })
    return account_info


def get_all_undone_order_counts(order_database) -> int:
    """
    获取有未完成的关注订单数

    :param order_database: 订单表对象
    :return: int
    """
    undone_order_counts = order_database.count_documents(
        {'order_state': {'$lt': 2}, 'sign': {'$lt': 3}, 'order_type': 1})  # 找到所有未完成的订单

    return undone_order_counts


def get_account_unfamiliar_order(order_database, one_account_info: dict,
                                 digg_value: int) -> list and dict:
    """
    获取当前机器人未点过的订单
    :param one_account_info:
    :param digg_value: 还可以点多少个赞
    :param order_database: 订单表对象
    :return: list or None
    """
    order_list = []
    is_digg_item_id_list = one_account_info['is_digg_item_id']

    for i in order_database.find(
            {"$and": [{'order_type': 1},
                      {'order_state': {'$ne': 2}},
                      {'sign': 1},
                      {"counts": {"$gt": 0}}
                      ]
             }, {"robots_num": 1, "counts": 1, "order_state": 1, "now_num": 1, "item_id": 1},
            no_cursor_timeout=True):

        if i['item_id'] not in is_digg_item_id_list:
            order_list.append(i)

    return order_list[:digg_value]


def get_day_digg_num(account_database, one_account_info: dict, max_digg_num=90) -> int:
    """
    获取账号当天还剩下的的关注数
    :param account_database: 账号表对象
    :param one_account_info: 当前提取出来的账号 -> dict
    :param max_digg_num: 一天最多的关注数
    :return:
    """
    if 'day_digg' in one_account_info:
        day_digg_list = one_account_info['day_digg']
        for i in day_digg_list:
            if i['date'] == str(datetime.date.today()):
                day_digg_num = max_digg_num - i['digg_counts']
                if day_digg_num <= 0:
                    return 0
                return day_digg_num

        day_digg_list.append({'date': str(datetime.date.today()), 'digg_counts': 0})
        account_database.find_one_and_update({'_id': one_account_info['_id']},
                                             {'$set': {'day_digg': day_digg_list}})
        return max_digg_num
    else:
        account_database.find_one_and_update({'_id': one_account_info['_id']},
                                             {'$set': {'day_digg': [
                                                 {'date': str(datetime.date.today()),
                                                  'digg_counts': 0}
                                             ]}})
        return max_digg_num


def account_cold_by_time(account_database, one_account_info, clod_time: int = 60):
    """
    指定账号冷却 clod_time 秒
    :param account_database: 账号表
    :param one_account_info: 账号信息
    :param clod_time: 冷却时间
    :return: None
    """
    account_database.find_one_and_update({'user_id': one_account_info['user_id']},
                                         {'$set': {'digg_status': 0,  # 还原状态
                                                   'digg_cold_time': int(time()) + clod_time,  # 冷却 10 分钟
                                                   }
                                          })


def get_start_info(order_database, account_database, log_helper, min_order_num: int) -> tuple or bool:
    """
    简化main()函数的长度 , 集中处理起始
    :param order_database: 订单表
    :param account_database: 机器人表 | 账号表
    :param log_helper: 单例日志对象
    :param min_order_num: 程序最小现在存订单启动阀值
    :return:
    """
    # 获取可操作的订单
    undone_order_counts = get_all_undone_order_counts(order_database)

    if undone_order_counts < min_order_num:
        log_helper.logger.info('订单不够')
        sleep(20)
        return False

    # 获取不在点关注工作中的robot account
    one_account_info = get_account(account_database)
    if not one_account_info:
        log_helper.logger.info('未获取到用户')
        sleep(20)
        return False

    digg_valve = get_day_digg_num(account_database, one_account_info, 400)
    if digg_valve <= 0:
        # 休眠一天
        log_helper.logger.info('机器人:{} ,点赞达到上限'.format(one_account_info['user_id']))
        account_cold_by_time(account_database, one_account_info, 60 * 60 * 24)
        return False

    # 获取当前机器人可以点赞的订单
    unfamiliar_order_list = get_account_unfamiliar_order(order_database, one_account_info, digg_valve)
    if not unfamiliar_order_list:
        log_helper.logger.info('机器人:{} ,无可点的订单，加3分钟冷却时间，切换机器人'.format(one_account_info['user_id']))
        account_cold_by_time(account_database, one_account_info, 60 * 3)
        return False

    return one_account_info, unfamiliar_order_list


def update_user_proxy(account_database, one_account_info, expire_time, proxies):
    """更新代理到用户信息中"""
    account_database.find_one_and_update({"user_id": one_account_info['user_id']},
                                         {"$set": {
                                             "expire_time": expire_time,
                                             "proxies": proxies
                                         }})


def update_day_digg_count(account_database, one_account_info):
    """更新今天的点赞数"""
    day_digg = account_database.find_one({"_id": one_account_info['_id']}, {"day_digg": 1})["day_digg"]
    if day_digg:
        # 没有当前日期的
        if day_digg[-1]["date"] < str(datetime.date.today()):
            day_digg.append({
                "date": str(datetime.date.today()),
                "digg_counts": 0,
            })

        for i in range(len(day_digg)):
            if day_digg[i]["date"] == str(datetime.date.today()):
                day_digg[i]["digg_counts"] += 1
                account_database.find_one_and_update({"_id": one_account_info['_id']},
                                                     {"$set": {"day_digg": day_digg}})
                break
    else:
        # day_digg没有数据
        day_digg.append({
            "date": str(datetime.date.today()),
            "digg_counts": 1,
        })
        account_database.find_one_and_update({"_id": account_database['_id']},
                                             {"$set": {"day_digg": day_digg}})


def verify_digg_res(digg_res, account_database, order_database, re_login_account_database, ban_account_database,
                    err_gather_database, log_helper, expire_time, one_account_info, proxies, item):
    """
    验证点赞结果
    :param digg_res:
    :param account_database:
    :param order_database:
    :param re_login_account_database:
    :param ban_account_database:
    :param err_gather_database:
    :param log_helper:
    :param expire_time:
    :param one_account_info:
    :param proxies:
    :param item:
    :return:
    """

    if digg_res['status_code'] == 0:
        if digg_res['is_digg'] == 0:
            # 点赞成功
            log_helper.logger.info('用户{}->订单{}点赞成功了'.format(one_account_info['user_id'], item['_id']))
            order_database.find_one_and_update({"_id": item['_id']}, {"$inc": {"now_num": 1, "counts": -1}})

            # 更新当前账号的已经点点赞列表
            click_digg_list = one_account_info['is_digg_item_id']
            click_digg_list.append(item['item_id'])
            account_database.find_one_and_update({'_id': one_account_info['_id']},
                                                 {'$set': {'is_digg_item_id': click_digg_list}})

            # 更新每日点点赞数
            update_day_digg_count(account_database, one_account_info)

            # 更新IP
            update_user_proxy(account_database, one_account_info, expire_time, proxies)
            return 0
        else:
            log_helper.logger.warning('用户{}->订单{}点赞失败了，冷却12小时'.format(one_account_info['user_id'], item['_id']))
            account_cold_by_time(account_database, one_account_info, 60 * 60 * 12)
            return 1

    elif digg_res["status_code"] == 8:
        log_helper.logger.warning("用户{}被从用户表里删除[NO COOKIE]，移到重新登录表".format(one_account_info['_id']))
        #  处理错误数据
        one_account_info.pop("_id")

        data = {"account_info": one_account_info, "digg_res": digg_res}
        err_gather_database.insert_one(data)

        re_login_account_database.insert_one(one_account_info)

        # account_database.delete_one({"user_id": one_account_info['user_id']})
        return 1
    elif digg_res["status_code"] == 9:
        log_helper.logger.warning("用户{}被从用户表里删除[NO USER]，移到小黑屋表".format(one_account_info['_id']))

        #  处理错误数据
        one_account_info.pop("_id")

        data = {"account_info": one_account_info, "digg_res": digg_res}

        err_gather_database.insert_one(data)

        ban_account_database.insert_one(one_account_info)
        account_database.delete_one({"user_id": one_account_info['user_id']})
        return 1
    elif digg_res["status_code"] == 2209:
        log_helper.logger.warning("作品{}已删除".format(item['item_id']))
        order_database.find_one_and_update({"_id": item["_id"]}, {"$set": {"order_state": 2, "error": "作品被删除"}})
        return 2
    elif digg_res["status_code"] == 2150:
        account_cold_by_time(account_database, one_account_info, 6 * 60)
        update_user_proxy(account_database, one_account_info, expire_time, proxies)
        log_helper.logger.info("手速过快，冷却6分钟".format(item['item_id']))
        return 1
    elif digg_res['status_code'] == 3059:

        one_account_info["status_code"] = 3059
        one_account_info.pop("_id")

        re_login_account_database.insert_one(one_account_info)

        # 删除数据
        account_database.delete_one({"user_id": one_account_info['user_id']})

        log_helper.logger.warning('用户{}出现点击验证码-已移库status_code=3059'.format(one_account_info['_id']))

        return 1
    elif digg_res['status_code'] == 3058:
        one_account_info.pop("_id")
        one_account_info["status_code"] = 3058
        re_login_account_database.insert_one(one_account_info)

        # 删除数据
        account_database.delete_one({"user_id": one_account_info['user_id']})

        log_helper.logger.warning('用户{}出现滑块验证码-已移库status_code=3058'.format(one_account_info['_id']))
        return 1
    else:
        one_account_info.pop("_id")
        data = {
            "user_id": one_account_info['user_id'],
            "digg_res": digg_res,
            "order_id": item['_id'],
            "item_id": item['item_id']
        }
        err_gather_database.insert_one(data)
        log_helper.logger.warning("出现没有写的情况记录到异常表")
        return 1


def add_robot(order_info, order_db):
    if "robots_num" not in order_info:
        order_db.find_one_and_update({"_id": order_info["_id"]}, {"$set": {"robots_num": 1}})
    else:
        order_db.find_one_and_update({"_id": order_info["_id"]}, {"$inc": {"robots_num": 1}})


def get_proxy(proxy_helper, log_helper):
    try:
        proxy_helper.get_proxy_ip_by_region()
        proxies = proxy_helper.get_proxy_info_format_requests()
        expire_time = int(mktime(strptime(proxy_helper.expire_time, "%Y-%m-%d %H:%M:%S")))
        return proxies, expire_time
    except KaYuException as ky:
        log_helper.logger.error(ky)
        sleep(5)
        return None, None


def change_and_verify_item(order_database, item):
    """判断是否存在item及修改状态值"""

    if item:
        item = order_database.find_one({"_id": item['_id']})  # 确保实时性，不然会导致点赞超标严重
        if item:
            robots_num = item['robots_num']
            counts = item['counts']
            if item["order_state"] == 0:
                order_database.find_one_and_update({'_id': item["_id"]}, {"$set": {"order_state": 1}})

            if counts < 1:
                order_database.find_one_and_update({"_id": item["_id"]}, {"$set": {"robots_num": 0}})

            # 进行中的机器人数大于剩余数就跳过当前订单
            if robots_num < counts:
                return item


def get_proxy_func(proxy_helper):
    try:
        proxy_helper.get_proxy_ip_by_region()
        proxy_city, expire_time, proxies = proxy_helper.get_proxy_info_format_requests()
        return {'proxy': proxies, 'city': proxy_city, 'expire_time': expire_time}
    except Exception as e:
        print(e)
        return None


item_test = ''


def digg(proxies, log_helper, encryption_http_server: DouYinEncryptionServerHelper):
    print(proxies)
    # 内部取值避免臃肿

    query_data = {'test': 0}
    res = TIKTOK_HOST.find(query_data)
    # print(res.count())
    random_num = random.randint(0, res.count())
    dumps_result = json.dumps(res[random_num], cls=JSONEncoder)
    json_result = json.loads(dumps_result)
    get_id = json_result["_id"]
    # TIKTOK_HOST.update_one({"_id": ObjectId(get_id)}, {"$set": {"test": 1}})

    item_id = json_result['item_id']
    item_test = item_id
    # print(res1)
    print(item_id)
    # item_id = '6758411443646844171'
    iid = '94769735096'
    did = "68495818160"
    openudid = 'd1e028b1d3ab8a11'
    ttreq = "1$36f6384173d9a38aef591487e18acca62946280a"

    d_ticket = '565974b29cc7a085a823f49067cb7ced1349a'
    uid_tt = 'f0ab927dde25613b9175c58cc908a9ac'
    odin_tt = "a566ab37eb1e4ff48761b17fdc6c36c3600588898488d2fef33d61adf5a4c3acaeeae4f55796de48d446810f966f77e36ad83f9acdb49a9050c72096008ae98a"
    sid_tt = '891d1be89d494377de38e7ababb6d65a'
    msh = '5T6TQaYAezhl6JR8wVh_-zO4fvg'
    session_key = '891d1be89d494377de38e7ababb6d65a'
    token = '00891d1be89d494377de38e7ababb6d65a5fb97c387835451dac2bb3f2edf7f9fe06f45489be1a6cdf3b0d73e09fc729944f'
    sid_guard = '891d1be89d494377de38e7ababb6d65a%7C1575604485%7C5184000%7CTue%2C+04-Feb-2020+03%3A54%3A45+GMT'
    # # 逻辑
    rticket = int(time() * 1000)

    # 正式版
    uuid_id = uuid.uuid4()
    url = ("https://aweme-hl.snssdk.com/aweme/v1/commit/item/digg/?aweme_id={item_id}&type=1&channel_id=0&os_api=24"
           "&device_type=EVA-AL10&ssmix=a&manifest_version_code=880&dpi=480&uuid=869285033941730&app_name=aweme"
           "&version_name=8.8.0&ts={ts}&app_type=normal&ac=wifi&channel=tengxun_new&update_version_code=8802"
           "&_rticket={rticket}&device_platform=android&iid={iid}&version_code=880&openudid={openudid}"
           "&device_id={device_id}&resolution=1080*1794&device_brand=HUAWEI&language=zh&os_version=7.0"
           "&aid=1128&mcc_mnc=46003").format(item_id=item_id, device_id=did, iid=iid,
                                             rticket=rticket, ts=int(rticket / 1000), openudid=openudid)

    # 正式版
    cookie = ("install_id={iid}; ttreq={ttreq}; odin_tt={odin_tt}; msh={msh}; d_ticket={d_ticket}; "
              "sid_guard={sid_guard}; uid_tt={uid_tt}; sid_tt={sid_tt}; "
              "sessionid={session_key}").format(d_ticket=d_ticket,
                                                iid=iid,
                                                ttreq=ttreq,
                                                sid_guard=sid_guard,
                                                uid_tt=uid_tt,
                                                odin_tt=odin_tt,
                                                msh=msh,
                                                sid_tt=sid_tt,
                                                session_key=session_key)

    try:
        Gorgon_res = encryption_http_server.Get_X_Gorgon(url, '', cookie, session_key)
        if not Gorgon_res:
            return 2
        khronos = Gorgon_res['X-Khronos']
        gorgon = Gorgon_res['X-Gorgon']
    except Exception as ex:
        print(ex)
        return 2

    # 极速版
    # headers = {
    #     'Host': 'aweme.snssdk.com',
    #     "Connection": "close",
    #     "Cookie": cookie,
    #     "X-SS-REQ-TICKET": str(int(time() * 1000)),
    #     "X-SS-TC": "0",
    #     "Accept-Encoding": "gzip, deflate",
    #     "User-Agent": ('com.ss.android.ugc.aweme.lite/{} (Linux; U; Android {}; zh_CN_#Hans; {}; '
    #                    'Build/{}; Cronet/58.0.2991.0)').format(version_code, os_version, device_type,
    #                                                            device_brand + device_type),
    #     'X-Gorgon': gorgon,
    #     'X-Khronos': khronos,
    # }

    # 正式版
    headers = {
        "Host": "aweme-hl.snssdk.com",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "X-SS-REQ-TICKET": str(int(time() * 1000)),
        "X-Tt-Token": token,
        "sdk-version": "1",
        "X-SS-DP": "1128",
        "User-Agent": "com.ss.android.ugc.aweme/880 (Linux; U; Android 7.0; zh_CN_#Hans; EVA-AL00; Build/HUAWEIEVA-AL10; Cronet/TTNetVersion:4d9f94e8 2019-10-29)",
        "x-tt-trace-id": "00-d96883da09ff2ab3db0170cb8a570468-d96883da09ff2ab3-01",
        "X-Gorgon": gorgon,
        "X-Khronos": khronos
    }
    try:
        res = requests.get(
            url=url,
            headers=headers,
            # proxies=proxies,
            timeout=15
        )
        if res.status_code == 200:
            res_data = res.json()
            if res_data.get("is_digg") == 1:
                TIKTOK_FAILED_ORDERS.insert_one(json_result)
                TIKTOK_HOST.delete_one({"_id": ObjectId(get_id)})
                return res.json()
            return res.json()
    except ProxyError as ex:
        print(ex)
        log_helper.logger.error("Digg Error {}".format(ex))
        return 1
    except (Timeout, ConnectionError, ConnectTimeout) as ex:
        log_helper.logger.error("Digg Error {}".format(ex))
        return 2


def digg(user, item_id, proxies, log_helper, encryption_http_server: DouYinEncryptionServerHelper):
    # 内部取值避免臃肿
    iid = user['iid']
    did = user['did']
    # sid_guard = user.get('sid_guard',"")
    # ttreq = user['ttreq']
    openudid = user['openudid']
    # odin_tt = user.get("odin_tt","")
    # uid_tt = user.get('uid_tt',"")
    # sid_tt = user.get('sid_tt',"")
    session_key = user.get('session_key', '')
    version_name = user.get('version_name', '')
    # device_brand = user['device_brand']
    # device_type = user['device_type']
    # version_code = user['version_code']
    # os_version = user['os_version']

    # 逻辑
    rticket = int(time() * 1000)

    url = ("https://aweme.snssdk.com/aweme/v1/commit/item/digg/?aweme_id={item_id}&type=1&retry_type=no_retry&"
           "iid={iid}&device_id={device_id}&ac=wifi&channel=xiaomi&aid=2329&app_name=douyin_lite&version_code=180&"
           "version_name=1.8.0&device_platform=android&ssmix=a&device_type=EVA-AL10&device_brand=HUAWEI&"
           "language=zh&os_api=24&os_version=7.0&openudid={openudid}&manifest_version_code=180&"
           "resolution=1080*1794&dpi=480&update_version_code=1800&_rticket={rticket}"
           "&ts={ts}").format(item_id=item_id, device_id=did, iid=iid,
                              rticket=rticket, ts=int(rticket / 1000), openudid=openudid)

    cookie = "qh[360]=1;install_id={};".format(session_key, iid)

    no_data_data = [{"os_api": 24},
                    {"device_platform": "android"},
                    {"device_type": "EVA-AL00"},
                    {"iid": iid},
                    {"ssmix": "a"},
                    {"manifest_version_code": 180},
                    {"dpi": 480},
                    {"version_code": 180},
                    {"app_name": "douyin_lite"},
                    {"version_name": "1.8.0"},
                    {"openudid": str(openudid)},
                    {"device_id": did},
                    {"resolution": "1080*1794"},
                    {"os_version": "7.0"},
                    {"language": "zh"},
                    {"device_brand": "HUAWEI"},
                    {"ac": "wifi"},
                    {"update_version_code": 1800},
                    {"aid": 2329},
                    {"channel": "xiaomi"}]

    try:
        no_data_res = encryption_http_server.get_url_no_data(int(rticket / 1000), url, no_data_data, did)
        if not no_data_res:
            return 2
        url = no_data_res
    except Exception as ex:
        print(ex)
        return 2

    try:
        Gorgon_res = encryption_http_server.Get_X_Gorgon(url, "", cookie, session_key)
        if not Gorgon_res:
            return 2
        khronos = Gorgon_res['X-Khronos']
        gorgon = Gorgon_res['X-Gorgon']
    except Exception as ex:
        print(ex)
        return 2

    headers = {
        'Host': 'aweme.snssdk.com',
        "Connection": "close",
        "Cookie": cookie,
        "X-SS-REQ-TICKET": str(int(time() * 1000)),
        "X-SS-TC": "0",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": 'com.ss.android.ugc.aweme.lite/180 (Linux; U; Android 7.0; zh_CN_#Hans; EVA-AL10; '
                      'Build/HUAWEI EVA-AL10; Cronet/58.0.2991.0)',
        # 'X-Gorgon': gorgon,
        # 'X-Khronos': khronos,
    }
    try:
        res = requests.get(
            url=url,
            headers=headers,
            proxies=proxies,
            verify=False,
            timeout=15,
        )
        if res.status_code == 200:
            return res.json()
    except ProxyError as ex:
        log_helper.logger.error("Digg Error {}".format(ex))
        return 1
    except (Timeout, ConnectionError, ConnectTimeout) as ex:
        log_helper.logger.error("Digg Error {}".format(ex))
        return 2


def socket_server():
    global socket_cmd
    server = socket.socket()
    server.bind(("192.168.100.2", 9632))
    server.listen()
    # 连接循环 可以不断接受新连接
    while True:
        clinet, addr = server.accept()
        # 通讯循环 可以不断的收发数据
        while True:
            try:
                # 如果是windows 对方强行关闭连接 会抛出异常
                # 如果是linux 不会抛出异常 会死循环收到空的数据包
                data = clinet.recv(1024)
                if not data:
                    clinet.close()
                    break
                if data.decode("utf-8") == "stop":
                    clinet.send("关闭成功，请等待10秒".encode("utf-8"))
                    socket_cmd = "stop"
                elif data.decode("utf-8") == "pause":
                    clinet.send("暂停成功，请等待10秒".encode("utf-8"))
                    socket_cmd = "pause"
                elif data.decode("utf-8") == "start":
                    clinet.send("开启成功".encode("utf-8"))
                    socket_cmd = "start"
                else:
                    clinet.send("错误指令".encode("utf-8"))

            except ConnectionResetError:
                print("关闭了客户端连接")
                clinet.close()
                break
    cliner.close()
    server.close()


def main(order_database, account_database, ban_account_database, re_login_account_database, err_gather_database,
         encryption_http_server, proxy_helper: ZiMaProxyHelper, log_helper, min_order_num: int = 50):
    counts_list = []
    item_list = []
    global socket_cmd
    while True:
        proxies = ""
        if socket_cmd == "pause":
            sleep(10)
            continue
        if socket_cmd == "stop":
            break

        # 基本信息获取
        start_info = get_start_info(order_database, account_database, log_helper, min_order_num)
        if not start_info:
            continue
        one_account_info, unfamiliar_order_list = start_info

        # 获取用户的历史代理
        if 'expire_time' in one_account_info:
            expire_time = one_account_info["expire_time"]
            if isinstance(expire_time, str) == True:
                expire_time = int(mktime(strptime(expire_time, "%Y-%m-%d %H:%M:%S")))
            if expire_time and expire_time - int(time()) >= 60 * 3:
                # 过期时间大于 3 分钟 就使用旧代理
                proxies = one_account_info['proxies']
                expire_time = one_account_info['expire_time']
            else:
                proxies, expire_time = get_proxy(proxy_helper, log_helper)
                if not proxies:
                    account_cold_by_time(account_database, one_account_info, 0)
                    continue
        else:
            proxies, expire_time = get_proxy(proxy_helper, log_helper)
            if not proxies:
                account_cold_by_time(account_database, one_account_info, 0)
                continue

        for item in unfamiliar_order_list:
            item = change_and_verify_item(order_database, item)  # 处理机器人数等
            if not item:
                continue

            # 可能在别的线程或上一次点赞或关注中被del 所以需要再次判断
            one_account_info = account_database.find_one({'_id': one_account_info['_id']})
            if not one_account_info:
                break
        item['item_id'] ="6765072331460201741"
        res1 =TIKTOK_HOST.find()
        counts =res1.count()
        num = random.randint(0, counts)
        print(res1[num]["item_id"])

        # 机器人+1 开始点赞
        try:
            # print(item['item_id'])
            # add_robot(item, order_database)
            sleep(1)
            digg_res = digg(proxies, log_helper, encryption_http_server)

            print(digg_res)
            while not digg_res or digg_res == 1 or digg_res == 2:

                if digg_res == 1:
                    proxies, expire_time = get_proxy(proxy_helper, log_helper)
                    if not proxies:
                        # account_cold_by_time(account_database, one_account_info, 0)
                        continue

                if digg_res == 2:
                    sleep(5)
                digg_res = digg(proxies, log_helper, encryption_http_server)
        finally:
            # 机器人-1 点赞结束
            order_database.find_one_and_update({"_id": item["_id"]}, {"$inc": {"robots_num": -1}})

            over_res = verify_digg_res(digg_res, account_database, order_database, re_login_account_database,
                                       ban_account_database, err_gather_database, log_helper, expire_time,
                                       one_account_info, proxies,
                                       item)

            if socket_cmd != "start":
                # 得到任何不为 开始的指令就跳出本次循环 然后 继续
                break
            if over_res == 2:
                # "继续结果"
                continue
            if over_res == 1:
                # "跳出结果，跳出前修改状态值"
                break
        if not one_account_info:
            continue

        update_user_proxy(account_database, one_account_info, expire_time, proxies)
        account_cold_by_time(account_database, one_account_info, 60 * 2)


if __name__ == '__main__':
    #     socket_server()
    config = IniFileHelper('../config.ini')
    client = pymongo.MongoClient(host=["192.168.100.2:27016"])
    data = client[config.get_val('DBClientInfo.database_name')]
    digg_order = data[config.get_val('DiggSetting.order_database_name')]

    account_database = client['aweme_server'][config.get_val('DiggSetting.account_database_name')]  # 用户表
    # account_database = data[config.get_val('DiggSetting.account_database_name')]  # 用户表
    ban_user_info = data[config.get_val('DiggSetting.ban_account_database_name')]  # 被ban的账号
    re_login = data[config.get_val('DiggSetting.re_login_account_database_name')]  # 重新登录表
    re_login_digg1 = data[config.get_val('DiggSetting.re_login1_account_database_name')]  # 重新登录表
    error_data = data[config.get_val('DiggSetting.err_gather_database_name')]  # 记录未出现的点赞失败情况
    encryption_http_server = DouYinEncryptionServerHelper(config.get_val("EncryptionServer.host"),
                                                          config.get_val("EncryptionServer.port"))
    proxy_helper = ZiMaProxyHelper(host="192.168.100.2:27016")

    log_helper = log_tool()
    log_helper.setlogger('log.txt', True)
    min_order_num = config.get_val('DiggSetting.min_start_order_num', isint=True)
    main(digg_order, account_database, ban_user_info, re_login, error_data,
         encryption_http_server, proxy_helper, log_helper, min_order_num)
