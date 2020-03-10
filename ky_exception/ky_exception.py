from enum import Enum
class KaYuException(BaseException):
    """
    通用的异常类，如果类的code（ErrorCode）的值为2则为无法恢复错误需要人工介入解决
    """
    class ErrorCode(Enum):
        可恢复错误 = 1
        无法恢复错误 = 2

    def __init__(self, text, code: ErrorCode):
        self.__text = text
        self.__code = code

    def __str__(self):
        return self.__text

    def get_text(self):
        """
        获取异常信息文本
        :return:
        """
        return self.__text

    def get_code(self):
        """
        获取异常code，为ErrorCode类型
        如果改类型的值为1则是可恢复错误，否则为不可恢复错误
        :return:
        """
        return self.__code