import time
from enum import Enum, unique
from urllib.parse import urlencode
import requests
from pymongo import MongoClient
from ky_exception.ky_exception import KaYuException


class ZiMaProxyHelper:
    @unique
    class ProxyCityInfo(Enum):
        甘肃省张掖市 = (620000, 620700)
        甘肃省庆阳市 = (620000, 621000)
        陕西省商洛市 = (610000, 611000)
        云南省临沧市 = (530000, 530900)
        云南省玉溪市 = (530000, 530400)
        云南省丽江市 = (530000, 530700)
        云南省大理白族自治州 = (530000, 532900)
        云南省昭通市 = (530000, 530600)
        云南省文山壮族苗族自治州 = (530000, 532600)
        云南省普洱哈尼族彝族自治县 = (530000, 530821)
        云南省楚雄市 = (530000, 532301)
        云南省曲靖市 = (530000, 530300)
        云南省怒江傈僳族自治州 = (530000, 533300)
        云南省德宏傣族景颇族自治州 = (530000, 533100)
        云南省保山市 = (530000, 530500)
        四川省雅安市 = (510000, 511800)
        四川省自贡市 = (510000, 510300)
        四川省德阳市 = (510000, 510600)
        四川省眉山市 = (510000, 511400)
        四川省乐山市 = (510000, 511100)
        四川省泸州市市辖区 = (510000, 510501)
        广东省广州市 = (440000, 440100)
        广东省河源市 = (440000, 441600)
        广东省茂名市 = (440000, 440900)
        广东省潮州市 = (440000, 445100)
        广东省江门市 = (440000, 440700)
        广东省东莞市 = (440000, 441900)
        # 广东省江门市 = (440000, 440700)
        # 广东省江门市 = (440000, 440700)
        广东省湛江市 = (440000, 440800)
        广东省珠海市 = (440000, 440400)
        湖南省益阳市 = (430000, 430900)
        湖北省十堰市 = (420000, 420300)
        河南省鹤壁市 = (410000, 410600)
        河南省焦作市 = (410000, 410800)
        山东省莱芜市 = (370000, 371200)
        山东省枣庄市 = (370000, 370400)
        山东省济南市 = (370000, 370100)
        山东省滨州市 = (370000, 371600)
        山东省威海市 = (370000, 371000)
        山东省潍坊市 = (370000, 370700)
        山东省泰安市 = (370000, 370900)
        山东省淄博市 = (370000, 370300)
        山东省日照市 = (370000, 371100)
        山东省烟台市 = (370000, 370600)
        江西省宜春市 = (360000, 360900)
        江西省新余市 = (360000, 360500)
        江西省分宜县 = (360000, 360521)
        江西省南昌市 = (360000, 360100)
        江西省萍乡市 = (360000, 360300)
        江西省赣州市 = (360000, 360700)
        江西省吉安市 = (360000, 360800)
        江西省九江市 = (360000, 360400)
        江西省上饶市 = (360000, 361100)
        江西省景德镇市 = (360000, 360200)
        江西省鹰潭市 = (360000, 360600)
        福建省南平市 = (350000, 350700)
        福建省厦门市 = (350000, 350200)
        福建省宁德市 = (350000, 350900)
        福建省漳州市 = (350000, 350600)
        福建省三明市 = (350000, 350400)
        安徽省池州市 = (340000, 341700)
        安徽省芜湖市 = (340000, 340200)
        安徽省合肥市 = (340000, 340100)
        安徽省马鞍山市 = (340000, 340500)
        安徽省宣城市 = (340000, 341800)
        安徽省六安市 = (340000, 341500)
        安徽省铜陵市 = (340000, 340700)
        安徽省蚌埠市 = (340000, 340300)
        安徽省黄山市 = (340000, 341000)
        安徽省亳州市 = (340000, 341600)
        安徽省阜阳市 = (340000, 341200)
        浙江省嘉兴市 = (330000, 330400)
        浙江省金华市 = (330000, 330700)
        浙江省绍兴市 = (330000, 330600)
        浙江省衢州市 = (330000, 330800)
        浙江省舟山市 = (330000, 330900)
        浙江省温州市 = (330000, 330300)
        浙江省台州市 = (330000, 331000)
        浙江省宁波市 = (330000, 330200)
        浙江省杭州市 = (330000, 330100)
        浙江省湖州市 = (330000, 330500)
        浙江省丽水市 = (330000, 331100)
        江苏省镇江市 = (320000, 321100)
        江苏省常州市 = (320000, 320400)
        江苏省盐城市 = (320000, 320900)
        江苏省淮安市 = (320000, 320800)
        江苏省连云港市 = (320000, 320700)
        江苏省徐州市 = (320000, 320300)
        江苏省泰州市 = (320000, 321200)
        江苏省无锡市 = (320000, 320200)
        江苏省宿迁市 = (320000, 321300)
        江苏省扬州市 = (320000, 321000)
        江苏省南通市 = (320000, 320600)
        江苏省南京市 = (320000, 320100)
        江苏省苏州市 = (320000, 320500)
        上海市闵行区 = (310000, 310112)
        辽宁省抚顺市 = (210000, 210400)
        辽宁省辽阳市 = (210000, 211000)
        辽宁省鞍山市 = (210000, 210300)
        辽宁省铁岭市 = (210000, 211200)
        辽宁省盘锦市 = (210000, 211100)
        辽宁省丹东市 = (210000, 210600)
        辽宁省阜新市 = (210000, 210900)
        辽宁省本溪市 = (210000, 210500)
        内蒙古呼和浩特市 = (150000, 150100)
        山西省晋城市 = (140000, 140500)
        山西省忻州市 = (140000, 140900)
        河北省保定市 = (130000, 130600)
        北京市朝阳区 = (110000, 110105)

    class ProxyTime(Enum):
        Minute5_25 = 1,
        Minute25_240 = 2,
        Hour3_6 = 3,
        Hour6_12 = 4,
        Hour48_72 = 5

    class ProxyYYS(Enum):
        # 未定义
        UnLimited = 0,
        # 中国联通
        联通 = 100026,
        # 中国电信
        电信 = 100027

    class ProxyProtocol(Enum):
        HTTP = 1,
        SOCK5 = 2,
        HTTPS = 11

    class ProxyIPType(Enum):
        IP_Dircet = 1,  # 直连IP
        IP_Tunnel = 2,  # 隧道IP

    def __init__(self, host, db_name="aweme_server", db_coll="zima_porxy_info"):
        self.__database = MongoClient(host=host)
        self.__proxy_coll = self.__database[db_name][db_coll]
        self.ip = None
        self.port = None
        self.expire_time = None
        self.city = None
        self.isp = None

    def get_proxy_ip_by_region(self):
        """
        获取指定地址的IP
        :param region:城市
        :return:
        """
        print("取代理了")
        return self.__get_proxy_by_region_in_database()

    def get_proxy_info_format_requests(self):
        """
        获取符合requests格式的代理
        :return:
        """
        return {"http": "http://{}:{}".format(self.ip, self.port),
                "https": "https://{}:{}".format(self.ip, self.port)}

    def __get_url_by_region_in_web(self):
        url = "http://http.tiqu.alicdns.com/getip3?num=400&type=2&pro=440000&city=0&yys=0&port=2&time=1&ts=1&ys=1&cs=1&lb=1&sb=0&pb=45&mr=2&regions=&gm=1"
        try:
            result = requests.get(url, timeout=20)
        except Exception:
            raise KaYuException("网络连接错误", KaYuException.ErrorCode.可恢复错误)
        if result.status_code == 200:
            data_json = result.json()
            if data_json["success"]:
                proxy_infos = data_json["data"]
                for data in proxy_infos:
                    if data.get("city") == '深圳市':
                        proxy_info = {
                            "ip": data.get("ip"),
                            "port": data.get("port"),
                            "expire_time": data.get("expire_time"),
                            "city": data.get("city"),
                            "isp": data.get("isp")
                        }
                        self.__proxy_coll.insert_one(proxy_info)
                return True
            else:
                code = data_json["code"]
                if code == 115:
                    raise KaYuException(result.json()["msg"], KaYuException.ErrorCode.可恢复错误)
        else:
            raise KaYuException(result.text, KaYuException.ErrorCode.可恢复错误)

    def __get_proxy_by_region_in_database(self):
        """
        从数据库中按城市获取 http 代理
        :param region: 城市
        :return:
        """
        proxy_infos = self.__proxy_coll.find({'city': '深圳市'})
        if proxy_infos:
            for data in proxy_infos:
                expire_time = data["expire_time"]
                # 如果过期时间小于3分钟
                if (time.mktime(time.strptime(expire_time, "%Y-%m-%d %H:%M:%S")) - int(time.time())) < 60 * 3:
                    self.__proxy_coll.delete_one(data)
                else:
                    self.__proxy_coll.delete_one(data)
                    # 返回统一格式的proxy数据
                    self.ip = data['ip']
                    self.port = data['port']
                    self.expire_time = data['expire_time']
                    self.city = data['city']
                    self.isp = data['isp']
                    return True
            else:
                self.__get_url_by_region_in_web()
                return self.__get_proxy_by_region_in_database()

    @staticmethod
    def __get_url_for_type(ip_type):
        url = ""
        if ip_type == ZiMaProxyHelper.ProxyIPType.IP_Dircet:
            url = "http://webapi.http.zhimacangku.com/getip?"
        elif ip_type == ZiMaProxyHelper.ProxyIPType.IP_Tunnel:
            url = "http://http.tiqu.alicdns.com/getip3?"
        return url
