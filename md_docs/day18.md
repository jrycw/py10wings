# [Day18] 六翼 - 導讀Descriptor HowTo Guide: How dot works?
## 六翼大綱
在經過前面數翼的洗禮後，我們具備了閱讀`Descriptor HowTo Guide`比較深入部份的知識了。

* [[Day18]](https://ithelp.ithome.com.tw/articles/10317770)介紹Python如何使用`dot`來`get`跟`set` `attribute`。
* [[Day19]](https://ithelp.ithome.com.tw/articles/10317771)導讀[Descriptor HowTo Guide的Pure Python Equivalents](https://docs.python.org/3/howto/descriptor.html#pure-python-equivalents)。

由於`attribute lookup`是一個複雜的主題，我們建議大家多看看不同高手的描述方法，可能比較容易心領神會。

除了`Descriptor HowTo Guide`外，我們特別推薦`Dr. Fred Baptiste`的[Python3:Deep Dive-Part4](https://www.udemy.com/user/fredbaptiste/)課程及`Ionel Cristian Mărieș`的[部落格文章](https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/)。

本翼筆記為嘗試交叉參考上述資料而做。由於本翼難度頗高，再加上有些自己試著修改的程式碼，如果有錯誤的話，還望諸位先進可以不吝斧正，相當感謝。

##  How dot works?
今天我們將分別理解四個層面的dot:
1. How obj.attr works(obj is instance)?
2. How obj.attr works(obj is class)?
3. How obj.attr=value works(obj is instance)?
4. How obj.attr=value works(obj is class)?(實驗性質，待研究)

至於`super().attr`，我們建議直接參考[`Guido`的tutorial](https://www.python.org/download/releases/2.2.3/descrintro/#cooperation)，但可能需要一些Python2的基礎，才能體會老爹於20年前建置`super()`的邏輯。但是即使是在有Python2及`descriptor`與`metaclasses`的基本知識下，這篇tutorial還是相當難啃呀! 期望未來有一天我們能靜下心來，像欣賞`Descriptor HowTo Guide`一樣，好好拜讀幾遍。

## 名詞定義
首先我們來看一段[Descriptor HowTo Guide](https://docs.python.org/3/howto/descriptor.html#overview-of-descriptor-invocation)開頭的描述：
> The Ten class is a descriptor whose `__get__()` method always returns the constant 10:...In the a.y lookup, the dot operator finds a descriptor instance, recognized by its `__get__` method. Calling that method returns 10.
```python=
class Ten:
    def __get__(self, obj, objtype=None):
        return 10

class A:
    x = 5                       
    y = Ten()  
```
可以看出`Raymond`明確地說明`Ten`是`descriptor`，而`y`是`descriptor instance`。雖然在大多數情況，我們會將`Ten`及`y`都稱作`descriptor`。

為了方便溝通，我們於`# 01`定義幾個名詞。
```python=
# 01
class NonDataDescriptor:
    def __get__(self, instance, owner_cls):
        ...


class DataDescriptor:
    def __get__(self, instance, owner_cls):
        ...

    def __set__(self, instance, value):
        ...


class DummyClass:
    a = 1


class MyClass(DummyClass):
    non_data_desc = NonDataDescriptor()
    data_desc = DataDescriptor()


if __name__ == '__main__':
    print(MyClass.__mro__)  # MyClass, DummyClass, object
    my_inst = MyClass()
```
* `NonDataDescriptor`為`Non-data descriptor`，而`non_data_desc`為其生成的`instance`。
* `DataDescriptor`是`data descriptor`，而`data_desc`為其生成的`instance`。
* 如果`obj.attr`在生成`obj`的`class`或其`MRO`上任一`class`的`__dict__`內，我們以`obj.attr in cls_mro`代稱，並以`base`來代稱`attr`所在的`class`。例如，`# 01`中的`my_inst.a`，因為`a`在`MyClass`(`type(my_inst)`)的`MRO`上的`DummyClass.__dict__`，我們會稱`my_inst.a in cls_mro`，而其`base`則為`DummyClass`。
* 如果`obj.attr`不在生成`obj`的`class`或其`MRO`上任一`class`的`__dict__`內，我們以`obj.attr not in cls_mro`代稱，
* 如果`obj`為`class`且如果`obj.attr`在`obj`的`class`或其`MRO`上任一`class`的`__dict__`內，我們以`obj.attr in obj_cls_mro`代稱，並以`obj_base`來代稱`attr`所在的`class`。例如，`# 01`中的`MyClass.a`，因為`a`在`MyClass`的`MRO`上的`DummyClass.__dict__`，我們會稱`MyClass.a in obj_cls_mro`，而其`obj_base`則為`DummyClass`。


## 1. How obj.attr works(obj is instance)?
[`object.__getattribute__`](https://docs.python.org/3/reference/datamodel.html#object.__getattribute__)是Python取得`attribute`值的`dunder method`。

### `object.__getattribute__`
下面是[`object.__getattribute__`](https://docs.python.org/3/howto/descriptor.html#invocation-from-an-instance)於Python的實作。
####  `find_name_in_mro`
`find_name_in_mro`接受三個參數：
* `cls`為生成`obj`的`class`。
* `name`為想尋找的`attribute`(`str`型態)。
* `default`為一預設值。

針對`cls.__mro__`打一個迴圈，依序在`MRO`上每個`class`的`__dict__`尋找有沒有`name`這個`attribute`，如果找到就馬上返回。當迴圈結束還是沒找到的話，則返回`default`。
```python=
def find_name_in_mro(cls, name, default):
    "Emulate _PyType_Lookup() in Objects/typeobject.c"
    for base in cls.__mro__:
        if name in vars(base):
            return vars(base)[name]
    return default
```
#### `object_getattribute`
* `object_getattribute`接受兩個參數，`obj`及`name`。
* 利用`object()`建立一個獨特的預設值`null`。
* `obj_type`為生成`obj`的`class`。
* `cls_var`為呼叫`find_name_in_mro`回傳的結果。注意，`cls_var`可以不是普通的`class variable`。也可以是`data_desc`或`non_data_desc`，因為他們也可以視為一種`class variable`，所以`Raymond`這樣命名。
* `descr_get`為試圖由生成`cls_var`的`class`內去取`__get__`(即測試`cls_var`的`class`是否為`descriptor`)。如果取不到的話則返回預設值`null`。
* 接下來依照註解，需要判斷最多四次，來決定如何取值。
    * 第一個判斷是看看`cls_var`是否為`data_desc`。判斷方法是確定`descr_get`不是`null`且生成`cls_var`的`class`中有`__set__`或是`__delete__`。如果符合的話，代表`cls_var`是`data_desc`，呼叫它的`__get__`來取值。可以使用`descr_get(cls_var, obj, objtype)`或是`cls_var.__get__(obj, objtype)`兩種語法。
    * 如果`cls_var`不是`data_desc`則進行第二個判斷。看看`obj`有沒有`__dict__`且`name`是否在`__dict__`中。如果是的話，代表`cls_var`是`instance variable`，使用`vars(obj)['attr']`取值。
    * 如果`cls_var`也不是`instance variable`則進行第三個判斷。如果`descr_get`不是`null`的話，代表`cls_var`是`non_data_desc`，呼叫它的`__get__`來取值。`descr_get(cls_var, obj, objtype)`或是`cls_var.__get__(obj, objtype)`兩種語法。
    * 如果`cls_var`也不是`non_data_desc`的話，則進行第四個判斷。如果`cls_var`不是`null`的話，代表其為`class varaible`，返回`cls_var`。
    * 如果`cls_var`是`null`的話，代表經過前面四次確認後，仍無法順利取值，`raise AttributeError`。

```python=
def object_getattribute(obj, name):
    "Emulate PyObject_GenericGetAttr() in Objects/object.c"
    null = object()
    objtype = type(obj)
    cls_var = find_name_in_mro(objtype, name, null)
    descr_get = getattr(type(cls_var), '__get__', null)
    if descr_get is not null:
        if (hasattr(type(cls_var), '__set__')
            or hasattr(type(cls_var), '__delete__')):
            return descr_get(cls_var, obj, objtype)     # data descriptor
    if hasattr(obj, '__dict__') and name in vars(obj):
        return vars(obj)[name]                          # instance variable
    if descr_get is not null:
        return descr_get(cls_var, obj, objtype)         # non-data descriptor
    if cls_var is not null:
        return cls_var                                  # class variable
    raise AttributeError(name)
```

### `object.__getattr__`
當`obj.attr` `raise AttributeError`後，Python會呼叫[`obj.__getattr__`](https://docs.python.org/3/reference/datamodel.html#object.__getattr__)作為最後一個補救措施(預設行為是直接`raise AttributeError`)，如果還是有`AttributeError`不能處理的話，則`raise AttributeError`給使用者。

由於`object.__getattribute__`的實作內，並未呼叫`object.__getattr__`，而是由Python自動偵測到`AttributeError`時呼叫。所以當顯性呼叫`obj.__getattribute__`或是`super().__getattribute__`時，`object.__getattr__`並不會被呼叫。

#### `getattr_hook`
* `getattr_hook`接受兩個參數，`obj`及`name`。
* 嘗試顯性呼叫`obj.__getattribute__`，當`raise AttributeError`時，查看生成`obj`的`class`是否有`__getattr__`。
    * 如果沒有的話。則`reraise AttributeError`。
    * 如果有的話，則使用`type(obj).__getattr__`。

這邊要檢查`type(obj)`是否有`__getattr__`的原因，可能是因為一般的`instance`是沒有`__getattr__`的。如果直接`return obj.__getattr__(name)`，會引起另一個`AttributeError`，那麼就需要另一個`try-catch`來處理，語法更為複雜。

```python=
def getattr_hook(obj, name):
    "Emulate slot_tp_getattr_hook() in Objects/typeobject.c"
    try:
        return obj.__getattribute__(name)
    except AttributeError:
        if not hasattr(type(obj), '__getattr__'):
            raise
    return type(obj).__getattr__(obj, name)             # __getattr__
```


### 流程整理格式1
我們試著將當`obj.attr`(`obj is instance`)的`lookup`流程寫下來。
* 如果`obj.attr in cls_mro`且`obj.attr`是`data_desc`，則使用`data_desc.__get__(obj, type(obj))`。
* 如果`obj.attr in vars(obj)`，則返回`vars(obj)['attr']`。
* 如果`obj.attr in cls_mro`且`obj.attr`是`non_data_desc`，則使用`non_data_desc.__get__(obj, type(obj))`。
* 如果`obj.attr in cls_mro`則為`class variable`，返回`vars(base)['attr']`。
* 如果還沒成功取值，`raise AttributeError`(自動呼叫`obj.__getattr__`)。

![inst_get1](https://py10wings.jp-osa-1.linodeobjects.com/day18/inst_get1.png)

### 流程整理格式2
`流程整理格式1`是根據`Raymond`的筆記整理的，`Dr. Fred Baptiste`則建議由`obj`是否在`cls_mro`來做為分支思考。
*  如果`obj.attr in cls_mro`:
    * 如果`obj.attr`是`data_desc`，則使用`data_desc.__get__(obj, type(obj))`。
    * 如果`obj.attr in vars(obj)`，則返回`vars(obj)['attr']`。
    * 如果`obj.attr`是`non_data_desc`，則使用`non_data_desc.__get__(obj, type(obj))`。
    * 剩下的必定是`class variable`，返回`vars(base)['attr']`。
* 如果`obj.attr not in cls_mro`:
    * 如果`obj.attr in vars(obj)`，則返回`vars(obj)['attr']`。
    * 如果`obj.attr not in vars(obj)`，則`raise AttributeError`(自動呼叫`obj.__getattr__`)。

![inst_get2](https://py10wings.jp-osa-1.linodeobjects.com/day18/inst_get2.png)


## 2. How obj.attr works(obj is class)?
`Descriptor HowTo Guide`講到[invocation from a class](https://docs.python.org/3/howto/descriptor.html#invocation-from-a-class)時，是這麼說的：
> The logic for a dotted lookup such as A.x is in `type.__getattribute__()`. The steps are similar to those for `object.__getattribute__()` but the instance dictionary lookup is replaced by a search through the class’s method resolution order. If a descriptor is found, it is invoked with `desc.__get__(None, A)`.

僅管文件中沒有提供相對應的Python程式碼。但是我們可以根據上面描述，試著實作看看。
```python=
# 02 Experiment code, not verified
def find_name_in_mro(cls, name, default):
    cls_mro = object.__getattribute__(cls, '__mro__')
    for base in cls_mro:
        base_dict = object.__getattribute__(base, '__dict__')
        if name in base_dict:
            return base_dict[name]
    return default

def type_getattribute(obj, name):
    ...
    _cls_var = find_name_in_mro(obj, name, null)
    if _cls_var is not null:
        if getattr(type(_cls_var), '__get__', null) is not null:
            return _cls_var.__get__(None, obj)  # descriptor(of any kind)
        return _cls_var  # class variable 

...
```
由於此時的`obj`是`class`，所以我們需要將整個思考邏輯往上推一層。現在`type_getattribute`的判斷式是針對`metaclasses`的`MRO`，而我們的`instance lookup`也因為往上推一層，而變成了`class` `MRO`的`lookup`，這也是整段程式唯一需要修改的地方。
* 由於需要使用`find_name_in_mro`做兩次`MRO`的搜尋，一次是於`metaclass`中，一次是於`class`中。當在`class`中搜尋中，如果使用了`obj.__mro__`或`obj.__dict__`，會造成`Recursion Error`。所以我們這邊改使用`object.__getattribute__`，這麼一來，新的`find_name_in_mro`就能同時適用於兩個情況。
* `_cls_var`為`class` `MRO`的搜尋結果。如果`_cls_var`不是`null`的話，代表其位於`class`或其`MRO`上任一`class`的`__dict__`中。我們可以利用與前面相同的技巧，看看`getattr(type(_cls_var), '__get__', null)`的回傳是否為`null`。
    * 如果回傳值不是`null`，就代表`_cls_var`為`descriptor`的`instance`，依照文件說明，可以返回`_cls_var.__get__(None, obj)`。由於我們只需要`_cls_var`的`__get__`，所以相當於要補抓任何型態的`descriptor instance`，包括`data_desc`與`non_data_desc`，
    * 如果回傳值是`null`，就代表`_cls_var`為`class variable`，直接返回即可。

### 測試
我們使用`type_getattribute`來作為`MyType`的`__getattribute__`，並確認於不同情況下可以成功取值。

```python=
# 02 Experiment code, not verified
...

class MyType(type):
    def __getattribute__(self, name):
        # confirm only call once for each dot access
        print(f'MyType.__getattribute__ is called for {name=}')
        return type_getattribute(self, name)


class NonDataDescriptor:
    def __get__(self, instance, owner_cls):
        return 10


class DataDescriptor:
    def __get__(self, instance, owner_cls):
        return 20

    def __set__(self, instance, value):
        ...


class MyType1(MyType):
    z = DataDescriptor()


class MyType2(MyType1):
    y = NonDataDescriptor()


class MyType3(MyType2):
    x = 1


class DummyClass:
    d = 'dummy'


class MyClass(DummyClass, metaclass=MyType3):
    a = 100
    b = NonDataDescriptor()
    c = DataDescriptor()


if __name__ == '__main__':
    print(f'{MyClass.x=}')  # 1
    print(f'{MyClass.y=}')  # 10
    print(f'{MyClass.z=}')  # 20
    print(f'{MyClass.a=}')  # 100
    print(f'{MyClass.b=}')  # 10
    print(f'{MyClass.c=}')  # 20
    print(f'{MyClass.d=}')  # 'dummy'
```
另外，也確認了當同一個`attr`出現於不同地方，也會依照我們寫下的邏輯來取值。

`# 02a`中由於`t`為位於`MyType`中的`data_desc`，優先級別最高。
```python=
# 02a
...

class MyType(type):
    t = DataDescriptor()

    def __getattribute__(self, name):
        return type_getattribute(self, name)


class MyClass(metaclass=MyType):
    t = 't_in_myclass'


if __name__ == '__main__':
    print(f'{MyClass.t=}')  # 20
```

`# 02b`、`# 02c`與`# 02d`都因為`MyType`中的`t`不是`data_desc`，而優先從`MyClass`中取值。
```python=
# 02b
...

class MyType(type):
    t = NonDataDescriptor()

    def __getattribute__(self, name):
        return type_getattribute(self, name)


class MyClass(metaclass=MyType):
    t = 't'


if __name__ == '__main__':
    print(f'{MyClass.t=}')  # 't'
```

```python=
# 02c
...

class MyType(type):
    t = NonDataDescriptor()

    def __getattribute__(self, name):
        return type_getattribute(self, name)


class MyClass(metaclass=MyType):
    t = DataDescriptor()


if __name__ == '__main__':
    print(f'{MyClass.t=}')  # 20
```

```python=
# 02d
...

class MyType(type):
    t = 't_in_mytype'

    def __getattribute__(self, name):
        return type_getattribute(self, name)


class MyClass(metaclass=MyType):
    t = NonDataDescriptor()


if __name__ == '__main__':
    print(f'{MyClass.t=}')  # 10
```

### 流程整理格式1
我們試著將當`obj.attr`(`obj is class`)的`lookup`流程寫下來。
* 如果`obj.attr in cls_mro`且`obj.attr`是`data_desc`，則使用`data_desc.__get__(obj, type(obj))`。
* 如果`obj.attr in obj_cls_mro`:
    * 如果`obj.attr`是`desc_inst`，則使用`desc.__get__(obj, type(obj))`。
    * 如果`obj.attr`不是`desc_inst`，則返回`vars(obj_base)['attr']`。
* 如果`obj.attr in cls_mro`且`obj.attr`是`non_data_desc`，則使用`non_data_desc.__get__(obj, type(obj))`。
* 如果`obj.attr in cls_mro`則為`class variable`，返回`vars(base)['attr']`。
* 如果還沒成功取值，`raise AttributeError`(自動呼叫`obj.__getattr__`)。

![class_get1](https://py10wings.jp-osa-1.linodeobjects.com/day18/class_get1.png)

### 流程整理格式2
*  如果`obj.attr in cls_mro`:
    * 如果`obj.attr`是`data_desc`，則使用`data_desc.__get__(obj, type(obj))`。
    * 如果`obj.attr in obj_cls_mro`:
        * 如果`obj.attr`是`desc_inst`，則使用`desc.__get__(obj, type(obj))`。
        * 如果`obj.attr`不是`desc_inst`，則返回`vars(obj_base)['attr']`。
    * 如果`obj.attr`是`non_data_desc`，則使用`non_data_desc.__get__(obj, type(obj))`。
    * 剩下的必定是`class variable`，返回`vars(base)['attr']`。
* 如果`obj.attr not in cls_mro`:
    * 如果`obj.attr in obj_cls_mro`:
        * 如果`obj.attr`是`desc_inst`，則使用`desc.__get__(obj, type(obj))`。
        * 如果`obj.attr`不是`desc_inst`，則返回`vars(obj_base)['attr']`。
    * 如果`obj.attr not in obj_cls_mro`則`raise AttributeError`(自動呼叫`obj.__getattr__`)。

![class_get2](https://py10wings.jp-osa-1.linodeobjects.com/day18/class_get2.png)

## 3. How obj.attr=value works(obj is instance)?
[`object.__setattr__`](https://docs.python.org/3/reference/datamodel.html#object.__setattr__)是Python設定`attribute`值的`dunder method`(`註1`)。

根據`Dr. Fred Baptiste`的說明，我們可以將`obj.attr=value`整理如下
### 流程整理格式
* 如果`obj.attr in cls_mro`且`obj.attr`是`data_desc`，則使用`data_desc.__set__(obj, value)`。
* 如果`obj.attr`有`__dict__`，則使用`obj.__dict__['attr']=value`。
* 如果`obj.attr`沒有`__dict__`，則`raise AttributeError`。

![inst_set1](https://py10wings.jp-osa-1.linodeobjects.com/day18/inst_set1.png)


### `object.__setattr__`
根據上面的流程整理，我們可以試著於Python中實作`object.__setattr__`。
* 如果`descr_get`與`descr_set`都不是`null`的話，代表`cls_var`是`data_desc`，使用其`__set__`來設定`attribute`值。可以使用`descr_set(cls_var, obj, value)`或`cls_var.__get__(obj, value)`兩種語法。
* 查看`obj`有沒有`__dict__`。如果有的話，使用`obj.__dict__[name] = value`新增或修改`attribute`。
* 如果上面兩點檢查都不符，則`raise AttributeError`。

```python=
# 03 Experiment code, not verified
def object_setattr(obj, name, value):
    null = object()
    objtype = type(obj)
    cls_var = find_name_in_mro(objtype, name, null)
    descr_get = getattr(type(cls_var), '__get__', null)
    descr_set = getattr(type(cls_var), '__set__', null)
    if descr_get is not null and descr_set is not null:
        descr_set(cls_var, obj, value)  # data descriptor
        return
    if hasattr(obj, '__dict__'):
        obj.__dict__[name] = value  # instance variable
        return
    raise AttributeError(name)

...
```

### 測試
我們使用`object_setattr`來作為`Character`中的`__setattr__`，並確認可以成功存取`instance variable`及使用`descriptor instance`。

```python=
# 03 Experiment code, not verified
...

class DataDescriptor:
    def __get__(self, instance, owner_cls):
        print('__get__ called')
        if instance is None:
            return self
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        print('__set__ called')
        instance.__dict__[self._name] = value

    def __set_name__(self, owner_cls, name):
        self._name = name


class Character:
    dog = DataDescriptor()

    def __init__(self, name):
        self.name = name

    def __setattr__(self, name, value):
        print(f'Character.__setattr__ is called for {name=}. {value=}')
        object_setattr(self, name, value)


if __name__ == '__main__':
    john_wick = Character('John Wick')
    print(john_wick.name)  # John Wick
    john_wick.dog = 'Daisy'  # __set__ called
    print(john_wick.dog)  # __get__ called, Daisy
    print(john_wick.__dict__)  # {'name': 'John Wick' 'dog': 'Daisy'}
```


## 4. How obj.attr=value works(obj is class)?
**本小節的程式碼純屬實驗性質，強烈不建議這麼寫。但通過這個實作，我們學習思考了很多，所以想要做個筆記，留下記錄。**

至於`obj.attr=value(obj is class)`需要`mutate` `obj.__dict__`(`mappingproxy`)，所以需要overwrite `type.__setattr__`。但是這麼做會於呼叫`setattr`時，造成`Recursion Error`，除非直接使用`type.__setattr__`，我們沒有想到適合的解決方法。

在看了這篇[stackoverflow](https://stackoverflow.com/questions/43739608/how-different-is-type-setattr-from-object-setattr)的討論及`C code`之後，了解自己暫時沒有能力於Python實作`type.__setattr__`。

既然無法`mutate` `obj.__dict__` ，我們嘗試每次需要`mutate`時都重新生成一個`class`，於是有了`# 04`。於每次`MyType.__setattr__`被呼叫時，複製`class`的資訊並加上新設定的`attribute`，接著利用`exec`重新產生新的`class`來取代原先的`class`。
```python=
# 04 Experiment code, not verified
def find_name_in_mro(cls, name, default):
    "Emulate _PyType_Lookup() in Objects/typeobject.c"
    for base in cls.__mro__:
        if name in vars(base):
            return vars(base)[name]
    return default


def type_setattr(obj, name, value):
    """Just exploring the magic of Python, don't do this..."""
    if hasattr(obj, '__dict__'):
        cls_name = obj.__name__
        cls_bases = obj.__mro__
        cls_dict = dict(vars(obj)) | {name: value}
        _globals = globals() | {'cls_name':  cls_name,
                                'cls_bases': cls_bases,
                                'cls_dict': cls_dict}
        meta = type(obj).__name__
        cls_body = f'{cls_name}={meta}(cls_name, cls_bases, cls_dict)'
        exec(cls_body, _globals, globals())
    else:
        raise AttributeError(name)

        
class MyType(type):
    def __setattr__(self, name, value):
        print(f'MyType.__setattr__ is called for {name=}. {value=}')
        type_setattr(self, name, value)

...
```
### 測試
這樣的寫法的確可以設定`class variable`及`descriptor`。從`id`比較中可以看出，於每次設定`attribute`時，都會新生成一個`MyClass`。
```python=
# 04 Experiment code, not verified
...

class DataDescriptor:
    def __get__(self, instance, owner_cls):
        if instance is None:
            return self
        return instance.__dict__.get(self._name)

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

    def __set_name__(self, owner_cls, name):
        self._name = name


class MyClass(metaclass=MyType):
    a = 'a'


if __name__ == '__main__':
    orig_cls_id = id(MyClass)
    print(MyClass.a)  # a
    MyClass.a = 'b'
    print(MyClass.a)  # b
    assert orig_cls_id != id(MyClass)

    MyClass.c = DataDescriptor()
    my_inst = MyClass()
    my_inst.c = 'c'
    print(my_inst.c)  # c
    print(MyClass.c)  # <__main__.DataDescriptor object at 0x0000014667AE6690>
```



## 備註
註1: Python有`object.__getattribute__`與`object.__getattr__` ，但只有`object.__setattr__`而沒有`object__setattribute__`。

註2: 本日流程圖為`ChatGPT`及[PlantUML](https://plantuml.com/en/)協作繪製而成。為方便排版，所有的double underscore都使用single underscore代替。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/06_desc_how_to/day18_dot)。