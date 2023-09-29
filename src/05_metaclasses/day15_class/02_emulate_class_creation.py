# 02
cls_dict = {}
cls_body = '''
def __init__(self, x):
    self.x = x
'''
exec(cls_body, globals(), cls_dict)  # populating cls_body into cls_dict
cls_name = 'MyClass'
cls_bases = ()
MyClass = type(cls_name, cls_bases, cls_dict)
