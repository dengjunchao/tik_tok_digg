
import configparser


class IniFileHelper:
    def __init__(self, file_name):
        self.__config_obj = configparser.ConfigParser()
        self.__config_obj.read(file_name)

    def get_val(self, so_str: str, isint: bool = False):
        '''
        通过Sectone 和 Option 来获取配置的val
        :param section: 配置的大项  ->[MysqlDB]
        :param option: 大项下的小项 -> host=0.0.0.0
        :param isint: 是否用将获取的值转换成 int 类型 （非int将会以str输出）
        :return: 输出结果 val 或 None
        '''
        section, option = self.__split_str(so_str)

        if section in self.__config_obj.sections():
            options = self.__config_obj.options(section)
            if option in options:
                if isint:
                    try:
                        val = self.__config_obj.getint(section, option)
                    except ValueError as valerr:
                        print(valerr.args[0])
                        val = self.__config_obj.get(section, option)

                else:
                    val = self.__config_obj.get(section, option)
                return val
            else:
                print('Option中不存在{}'.format(option))
                raise IniNotFindOptionError()
        else:
            print('Section中不存在{}'.format(section))
            return IniNotFindSectionError()

    def __split_str(self, so_str: str):
        split_res = so_str.split('.')
        if len(split_res) != 2:
            raise IniKeyValError()
        else:
            if split_res[0] and split_res[1]:
                # 正常
                return split_res[0], split_res[1]
            else:
                raise IniKeyValError()


class IniKeyValError(Exception):
    def __init__(self):
        self.args = ('传参异常 格式为Section.Option 不可为空',)
        self.message = '传参异常 格式为Section.Option 不可为空'


class IniNotFindSectionError(Exception):
    def __init__(self):
        self.args = ('传参异常 Section不存在于配置文件',)
        self.message = '传参异常 Section不存在于配置文件'


class IniNotFindOptionError(Exception):
    def __init__(self):
        self.args = ('传参异常 Option不存在于配置文件',)
        self.message = '传参异常 Option不存在于配置文件'

# if __name__ == '__main__':
#     i = IniFileHelper()
#     print(i.get_val('mangoDB_config.port', isint=True))
so = '3430343437373331313334'