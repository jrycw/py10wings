# 10
eg = ExceptionGroup("eg", [TypeError(12)])
eg.foo = 'foo'
try:
    raise eg
except* TypeError as e:
    e.foo = 'bar'
print(eg.foo)  # 'foo'
