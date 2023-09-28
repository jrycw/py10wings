# 02
class MyType(type):
    mcls_var_x = 'x'

    def __prepare__(cls, cls_bases, **kwargs):
        cls_dict = {'cls_var_a': 'a'}
        return cls_dict

    def __new__(mcls, cls_name, cls_bases, cls_dict, **kwargs):
        cls_dict['cls_var_c'] = 'c'
        cls = super().__new__(mcls, cls_name, cls_bases, cls_dict)
        cls.say_hello = lambda self: 'MyType works!'
        return cls

    def __init__(cls, cls_name, cls_bases, cls_dict, **kwargs):
        cls.cls_var_d = 'd'

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.inst_var_c = 'c'
        return instance


class MyParentClass:
    cls_var_e = 'e'

    def good_morning(self):
        return 'Good morning!'


class MyClass(MyParentClass, metaclass=MyType):
    cls_var_b = 'b'

    def __new__(cls, b):
        instance = super().__new__(cls)
        instance.inst_var_a = 'a'
        return instance

    def __init__(self, b):
        self.inst_var_b = b


if __name__ == '__main__':
    my_inst = MyClass('b')
    cls_vars = {k: v
                for k, v in vars(MyClass).items()
                if k.startswith('cls_')}
    # {'cls_var_a': 'a', 'cls_var_b': 'b', 'cls_var_c': 'c', 'cls_var_d': 'd'}
    print(cls_vars)

    inst_vars = vars(my_inst)
    # {'inst_var_a': 'a', 'inst_var_b': 'b', 'inst_var_c': 'c'}
    print(inst_vars)

    # MyType.__new__
    print(my_inst.say_hello())  # MyType works!

    # MyParentClass
    print(my_inst.cls_var_e, MyClass.cls_var_e)  # e e
    print(my_inst.good_morning())  # Good morning!

    # MyType
    print(MyClass.mcls_var_x)  # x
    # print(my_inst.mcls_var_x)  # AttributeError

    # (<class '__main__.MyType'>, <class 'type'>, <class 'object'>)
    print(type(MyClass).__mro__)

    # (<class '__main__.MyClass'>, <class '__main__.MyParentClass'>, <class 'object'>)
    print(MyClass.__mro__)
