import requests
import threading
# 压力测试

def yal():
    #(requests.post(url="http://192.168.100.237:9900/encrypt_gzip", json={"data": {"magic_tag": "ss_app_log", "header": {"display_name": "抖音短视频", "update_version_code": 7102, "manifest_version_code": 710, "aid": 1128, "channel": "aweGW", "appkey": "57bfa27c67e58e7d920028d3", "package": "com.ss.android.ugc.aweme", "app_version": "7.1.0", "version_code": 710, "sdk_version": "2.5.5.8", "os": "Android", "os_version": "7.0", "os_api": 24, "device_model": "EVA-AL10", "device_brand": "HUAWEI", "device_manufacturer": "HUAWEI", "cpu_abi": "armeabi-v7a", "build_serial": "KWG7N16325003540", "release_build": "15b0850_20190711", "density_dpi": 480, "display_density": "mdpi", "resolution": "1794x1080", "language": "zh", "mc": "e0:a3:ac:fe:ef:ac", "timezone": 8, "access": "wifi", "not_request_sender": 0, "carrier": "中国电信", "mcc_mnc": "46003", "rom": "EMUI-EmotionUI_5.0.3-C00B399SP17", "rom_version": "EmotionUI_5.0.3_EVA-AL10C00B399SP17", "sig_hash": "aea615ab910015038f73c47e45d21466", "openudid": "86f11db8444f4b27", "clientudid": "482b5103-33b0-4389-813b-fa53dc179def", "serial_number": "KWG7N16325003540", "sim_serial_number": [], "region": "CN", "tz_name": "Asia\\/Shanghai", "tz_offset": 28800, "sim_region": "cn"}, "_gen_time": 1567226887780}}).json())
    print(requests.post(url="http://192.168.100.119:9700/encrypt_gzip", json={"data": {"magic_tag": "ss_app_log", "header": {"display_name": "抖音短视频", "update_version_code": 7102, "manifest_version_code": 710, "aid": 1128, "channel": "aweGW", "appkey": "57bfa27c67e58e7d920028d3", "package": "com.ss.android.ugc.aweme", "app_version": "7.1.0", "version_code": 710, "sdk_version": "2.5.5.8", "os": "Android", "os_version": "7.0", "os_api": 24, "device_model": "EVA-AL10", "device_brand": "HUAWEI", "device_manufacturer": "HUAWEI", "cpu_abi": "armeabi-v7a", "build_serial": "KWG7N16325003540", "release_build": "15b0850_20190711", "density_dpi": 480, "display_density": "mdpi", "resolution": "1794x1080", "language": "zh", "mc": "e0:a3:ac:fe:ef:ac", "timezone": 8, "access": "wifi", "not_request_sender": 0, "carrier": "中国电信", "mcc_mnc": "46003", "rom": "EMUI-EmotionUI_5.0.3-C00B399SP17", "rom_version": "EmotionUI_5.0.3_EVA-AL10C00B399SP17", "sig_hash": "aea615ab910015038f73c47e45d21466", "openudid": "86f11db8444f4b27", "clientudid": "482b5103-33b0-4389-813b-fa53dc179def", "serial_number": "KWG7N16325003540", "sim_serial_number": [], "region": "CN", "tz_name": "Asia\\/Shanghai", "tz_offset": 28800, "sim_region": "cn"}, "_gen_time": 1567226887780}}).json())


def main():
    while True:
        try:
            yal()
        except Exception as ex:
            print(ex)


lis = []

for _ in range(7):
    lis.append(threading.Thread(target=main))
for i in lis:
    i.start()
for i in lis:
    i.join()
