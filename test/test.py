from time import time

import pymongo
import requests

from soures.aweme_http_client import DouYinEncryptionServerHelper
from soures.config_helper import IniFileHelper

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
proxies = {
        "http" : "http://58.218.92.65:9687",
        "https" : "https://58.218.92.65:9687"
    }
# 内部取值避免臃肿
iid = 94071435446
did = 70061709230
sid_guard = user.get('sid_guard', "")
ttreq = user['ttreq']
openudid = user['openudid']
odin_tt = user.get("odin_tt", "")
uid_tt = user.get('uid_tt', "")
sid_tt = user.get('sid_tt', "")
session_key = user['session_key']
device_brand = user['device_brand']
device_type = user['device_type']
version_code = user['version_code']
os_version = user['os_version']
item_id = ''
rticket = int(time() * 1000)
url = 'https://api.amemv.com/aweme/v1/commit/item/digg/?aweme_id={item_id}&type=1&retry_type=no_retry' \
      '&iid={iid}&device_id={device_id}&ac=wifi&channel=xiaomi&aid=2329&app_name=douyin_lite&version_code=180' \
      '&version_name=1.8.0&device_platform=android&ssmix=a&device_type=EVA-AL00&device_brand=HUAWEI&language=zh' \
      '&os_api=24&os_version=7.0&uuid=355757561019213&openudid={openudid}&manifest_version_code=180' \
      '&resolution=1080*1794&dpi=480&update_version_code=1800&_rticket={rticket}&ts={ts}'.format(item_id=item_id,
                                                                                                device_id=did,
                                                                                                iid=iid,
                                                                                                rticket=rticket,
                                                                                                ts=int(
                                                                                                    rticket / 1000),
                                                                                                openudid=openudid)
cookie = ('install_id={iid}; ttreq={ttreq}; '
          'qh[360]=1; d_ticket=f5f37804a5c00981a06b85b90dc9ad9445c3f; '
          'odin_tt={odin_tt'
          'msh=8Mq3TIJ__FDex6OUkANI6et2rEs; '
          'sid_guard={sid_guard} '
          'uid_tt={uid_tt}; sid_tt={sid_tt}; '
          'sessionid={session_key}').format(sid_guard=sid_guard, uid_tt=uid_tt, odin_tt=odin_tt, sid_tt=sid_tt,
                                            session_key=session_key,
                                            iid=iid, ttreq=ttreq)
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
        print('没有加密成功')
    url = no_data_res
except Exception as ex:
    print(ex)

try:
    Gorgon_res = encryption_http_server.Get_X_Gorgon(url, "", cookie, session_key)
    if not Gorgon_res:
        print('没有加密成功1')
    khronos = Gorgon_res['X-Khronos']
    gorgon = Gorgon_res['X-Gorgon']
except Exception as ex:
    print(ex)

headers = {
    'Host': 'api.amemv.com',
    'Connection': 'keep-alive',
    'Cookie': cookie,
    'Accept-Encoding': 'gzip',
    'X-SS-TC': '0',
    'User-Agent': 'com.ss.android.ugc.aweme.lite/190 (Linux; U; Android 5.1.1; zh_CN; OPPO R11; Build/NMF26X;'
                  ' Cronet/58.0.2991.0)',
    'X-Gorgon': gorgon,
    'X-Khronos': khronos
}

res = requests.get(url, headers=headers)
print(res.content)
