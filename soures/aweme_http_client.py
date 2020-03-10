import requests
import json


class DouYinEncryptionServerHelper:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def Get_X_Gorgon(self, url: str, stub: str, cookies, session_id=""):
        post_url = 'http://{}:{}/X-Gorgon'.format(self.ip, self.port)
        data = {
            "url": url,
            "X-SS-STUB": stub,
            "cookies": cookies,
            "session_id": session_id
        }
        try:
            r = requests.post(post_url, json=data)
            if r and r.status_code == 200:
                return r.json()["result"]
        except Exception as ex:
            print('Get_X_Gorgon--错误{}'.format(ex))
            return False

    def get_stub_str(self, data):
        """
        获取请求头中的X-SS-STUB参数的数据。
        :param data: 加密后的数据，调用get_encrypt_data获取
        :return:result中存储了 X-SS-STUB的值
        :rtype: str
        """
        post_url = 'http://{}:{}/x_ss_stub_str'.format(self.ip, self.port)
        dict_data = {
            "data": data
        }
        try:
            r = requests.post(post_url, json=dict_data)
            if r and r.status_code == 200:
                return r.json()['result']
        except Exception as ex:
            print('X-SS-STUB-Str--错误{}'.format(ex))
            return False

    def get_url_no_data(self, server_time, url, data: list, device_id: int):

        post_url = 'http://{}:{}/get_url_no_data'.format(self.ip, self.port)
        dict_data = {
            "server_time": server_time,
            "url": url,
            "data": data,
            "device_id": device_id
        }
        try:
            r = requests.post(post_url, json=dict_data)
            if r and r.status_code == 200:
                return r.json()['data']
        except Exception as ex:
            print('get_url_no_data--错误{}'.format(ex))
            return False
