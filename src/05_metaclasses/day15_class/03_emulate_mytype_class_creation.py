# 03
class MyType(type):
    def __new__(mcls, cls_name, _cls_bases, cls_dict):
        cls = super().__new__(mcls, cls_name, _cls_bases, cls_dict)
        return cls


cls_dict = {}
cls_body = '''
def __init__(self, x):
    self.x = x
'''
exec(cls_body, globals(), cls_dict)  # populating cls_body into clas_dict
cls_name = 'MyClass'
cls_bases = ()
MyClass = MyType(cls_name, cls_bases, cls_dict)
print(type(MyClass))  # <class '__main__.MyType'>
