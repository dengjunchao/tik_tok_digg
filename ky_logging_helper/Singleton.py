# coding=utf-8
import sys

# 方法1,实现__new__方法
# 并在将一个类的实例绑定到类变量_instance上,
# 如果cls._instance为None说明该类还没有实例化过,实例化该类,并返回
# 如果cls._instance不为None,直接返回cls._instance
class singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance


# 使用__metaclass__（元类）的高级python用法
class singleton_ex(type):
    def __init__(cls, name, bases, dict):
        super(singleton_ex, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(singleton_ex, cls).__call__(*args, **kw)
        return cls._instance


# 测试
class singleton_demo(singleton):
    a = 1


class singleton_exemo(object):
    __metaclass__ = singleton_ex


if __name__ == "__main__":
    # 实例化数据库对象
    one = singleton_demo()
    two = singleton_demo()
    print(one == two)
    # 实例化数据库对象
    one_ex = singleton_exemo()
    two_ex = singleton_exemo()
    print(one_ex == two_ex)
