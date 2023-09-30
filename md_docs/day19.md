# [Day19] 六翼 - 導讀Descriptor HowTo Guide: Pure Python Equivalents

今天讓我們繼續跟著大神的腳步，一起閱讀[Descriptor HowTo Guide的Pure Python Equivalents](https://docs.python.org/3/howto/descriptor.html#pure-python-equivalents)，來看看如何用Python實作`property`、`function and bound method`, `staticmethod`、`classmethod`及`__slots__`。

## property
* `__init__`中接收`fget`、`fset`、`fdel`及`doc`四個選擇性給予的變數。如果沒有給`doc`但是`fget`內有的話，會取`fget`的`doc`作為`doc`。所以當我們使用`@Property`來裝飾一個`function`時，其實就是指定該`function`為`Property`的第一個變數`fget`。
* `__set_name__`會將`property` `instance`於`class`中的名字傳進來。
```python=
class Property:
    "Emulate PyProperty_Type() in Objects/descrobject.c"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self._name = ''

    def __set_name__(self, owner, name):
        self._name = name
    ...
```
* `property`實作有`__get__`、`__set__`及`__delete__`，所以就算沒有給定`fset`或`fdel`，仍然是一個`data descriptor`。
* `__get__`中，先檢查`obj`是否為`None`。如果是`None`的話，則表示是由`class`所呼叫，會返回`property` `instance`本身。接著檢查是否已有指定`self.fget`，如果沒有指定的話，則`raise AttributeError`。最後呼叫`self.fget`執行其`getter`的工作。
* `__set__`中，檢查是否已有指定`self.fset`，如果沒有指定的話，則`raise AttributeError`。最後呼叫`self.fset`執行其`setter`的工作。
* `__delete__`中，檢查是否已有指定`self.fdel`，如果沒有指定的話，則`raise AttributeError`。最後呼叫`self.fdel`執行其`deleter`的工作。
```python=
class Property:
    ...
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f"property '{self._name}' has no getter")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError(f"property '{self._name}' has no setter")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError(f"property '{self._name}' has no deleter")
        self.fdel(obj)
```
* `getter`、`setter`與`deleter`三種`function`的內容非常像。原則就是每次都建立一個新的`property` `instance`。舉`getter`為例，` type(self)`其實就是`property`這個`class`，我們將傳入的`fget`指定為`Property`的第一個參數`fget`，剩餘的`self.fset`、`self.fdel`及 `self.__doc__`就從`self`內來取。接著需要手動更新`property` `instance`的`_name`，因為`class`內有`__set_name__`的`attribute`只會在`class`被定義時呼叫一次(`註1`)，所以當我們後續利用`getter`、`setter`或`deleter`介面加入新`function`到`property` `instance`時，需自己更新。這麼一來就可以像是疊加一樣，彈性地加入需要的`function`。


```python=
class Property:
    ...
    
    def getter(self, fget):
        prop = type(self)(fget, self.fset, self.fdel, self.__doc__)
        prop._name = self._name
        return prop

    def setter(self, fset):
        prop = type(self)(self.fget, fset, self.fdel, self.__doc__)
        prop._name = self._name
        return prop

    def deleter(self, fdel):
        prop = type(self)(self.fget, self.fset, fdel, self.__doc__)
        prop._name = self._name
        return prop
```

## function and bound method
`method`與`function`不同的點是，`method`會自動傳入呼叫它的`instance`作為第一個參數，就是我們習慣的`self`。當由`instance`呼叫在`class`中的`function`時，其會變成一個`bound method`(`bound`在`self`上)。

`types.MethodType`可以幫助我們生成`bound method`:
* `MethodType`的`__init__`接受兩個參數，分別為`function`與要`bound`的對象。
* `MethodType`的`__call__`呼叫`self.__func__`，並以`self.__self__`作為第一個參數，`__call__`中所接受`*args`及`**kwargs`為剩餘參數，會並傳計算結果。

```python=
class MethodType:
    "Emulate PyMethod_Type in Objects/classobject.c"

    def __init__(self, func, obj):
        self.__func__ = func
        self.__self__ = obj

    def __call__(self, *args, **kwargs):
        func = self.__func__
        obj = self.__self__
        return func(obj, *args, **kwargs)
```
至於`function`，因為實作有`__get__`，是`non-data descriptor`。
* `function`的`__get__`中，先檢查`obj`是否為`None`。如果是`None`的話，則表示是由`class`來取，會返回`function` `instance`本身。如果不是`None`的話，則回傳一個`MethodType`生成的`method`。這個`method`是一個`bound method`，幫助我們將`function` `instance`與呼叫其的`instance` `bound`在一起。

```python=
class Function:
    ...

    def __get__(self, obj, objtype=None):
        "Simulate func_descr_get() in Objects/funcobject.c"
        if obj is None:
            return self
        return MethodType(self, obj)
```
假設我們現在有以下程式碼，我們來拆解看看，呼叫`my_instance.my_func(1, 2)`的整個流程。
```python=
class MyClass:
    def my_func(self, a, b):
        ...

my_inst = MyClass()
my_inst.my_func(1, 2)
```
* 由於`my_inst.my_func`是個`non_data_desc`，所以`my_inst`會先尋找`my_inst.__dict__`中有沒有`my_func`。 因為沒有找到，所以會使用`my_func`的`__get__`。
* 由於是從`my_inst`來取`my_func`，所以會回傳一個`MethodType`生的`bound method`，這個`method`將`my_func`與`my_inst` `bound`在一起。
* 當我們真正呼叫`my_inst.my_func(1, 2)`相當於使用`bound method`中的`__call__`，它會將`my_inst`作為`my_func`的第一個參數，`1`與`2`作為`my_func`的剩餘參數，然候回傳計算結果。這就是為什麼我們可以使用`my_inst.my_func(1, 2)`，而不需使用`my_inst.my_func(my_inst, 1, 2)`的由來。

一個有趣的事實是，`function`的`__get__`每次由`instance`呼叫時，都會回傳一個新的`MethodType` `instance`，這代表:
```python=
>>> my_inst.my_func is my_inst.my_func # False
>>> my_inst.my_func.__func__ is my_inst.my_func.__func__ # True
```
或許這會讓您意外，但這正是Python巧妙的設計，底層是同一個`function`，但是每次由`my_inst.my_func`來取時，都新生成一個`bound method`。Welcome to Python!

## staticmethod
適合使用`staticmethod`的`function`，代表其功能與`instance`或是`class`沒有關係。`staticmethod`可以幫忙裝飾底層`function`，使得我們無論是由`instance`或是`class`呼叫，都能使用相同的`signature`。
* `__init__`中，`staticmethod`接收一個`function`，並利用`functools.update_wrapper`來將`function`的`metadata`更新給`staticmethod` 的`instance`。
* 由於`staticmethod`有實作`__get__`，所以是一個`non-data descriptor`。無論是由`instance`或是由`class`來取，都返回`self.f`。
* `__call__`中，`self.f`不用`bound`到任何`obj`，直接搭配`___call__`接收的`*args`及`**kwds`，回傳結果即可。
```python=
import functools

class StaticMethod:
    "Emulate PyStaticMethod_Type() in Objects/funcobject.c"

    def __init__(self, f):
        self.f = f
        functools.update_wrapper(self, f)

    def __get__(self, obj, objtype=None):
        return self.f

    def __call__(self, *args, **kwds):
        return self.f(*args, **kwds)
```
## classmethod
`classmethod`可以將`class`中的`function`所`bound`的對象，由預設的`instance`改為`class`。
* `classmethod`的`__init__`與`staticmethod` `__init__`是一樣的。其接收一個`function`，並利用`functools.update_wrapper`來將`function`的`metadata`更新給`classmethod` 的`instance`。
* 由於`classmethod`有實作`__get__`，所以是一個`non-data descriptor`。當`cls`是`None`時，代表是由`obj`來取，所以利用`type(obj)`來取得其`cls`。接下來一樣使用`MethodType`回傳一個`bound method`，只是這次是將`self.f` `bound`給`cls`。
* `__get__`有一段被宣告將廢棄的程式碼，其原意是希望能串聯多個`decorator`。但是Python社群實際使用後發現，這樣的用法會產生許多[潛在問題](https://github.com/python/cpython/issues/89519)，Raymond也指出允許這樣的行為可能是一種[錯誤](https://github.com/python/cpython/issues/89519#issuecomment-1093931550)。

```python=
import functools

class ClassMethod:
    "Emulate PyClassMethod_Type() in Objects/funcobject.c"

    def __init__(self, f):
        self.f = f
        functools.update_wrapper(self, f)

    def __get__(self, obj, cls=None):
        if cls is None:
            cls = type(obj)
        if hasattr(type(self.f), '__get__'):
            # This code path was added in Python 3.9
            # and was deprecated in Python 3.11.
            return self.f.__get__(cls, cls)
        return MethodType(self.f, cls)
```

## `__slots__`
由於`__slots__`的實作需要用到`C`的`structure`及處理記憶體配置，所以Raymond說我們只能盡量仿效，以一個`_slotvalues`的`list`來替代真正的`slot` `structure`。

`__slots__`的實作比較複雜，共分為五個部份:
1. 建立`Member` `class`，此為一個`data descriptor`，用來控制已寫在`slot_names`內`attribute`的存取。
2. 建立`Type` `metaclass`，其功用為針對`slot_names`中所列名字，建立`class variable`，並將其值指為相對應的`Member` `instance`。
3. 建立`Object` `class`，其功用為設定`_slotvalues`(相當於模擬配置`__slots__`的記憶體)及當設定或刪除不在`slot_names`內的`attribute`時，需`raise AttributeError`。
4. 建立可用的`H` `class`，將使用`Type`為其`metaclass`，並繼承`Object`。
5. 由`H`生成`h` `instance`，實際測試使用。

### 1. Member
`Member`是一個具有`__get__`、`__set__`及`__delete__`的`data descriptor`。
* `__init__`中接收三個變數，分別為其在`class`中的名字，`class` `name`及其位於`_slotvalues`中的`index`。
* `__get__`中一樣先檢查`obj`是否為`None`。如果是`None`的話，則表示是由`class`來取，會返回`Member` `instance`本身。接著透過`self.offset `為`index`向`obj._slotvalues`取值。如果取回來的是預設的`sentinel`值`null`的話，表示該`index`值沒被正確指定又或者已經被刪除，`raise AttributeError`。最後，如果通過上述檢查的話，則返回所取之值。
* `__set__`中直接指定`value`到`obj._slotvalues`的`self.offset`位置。
* `__delete__`中於`__get__`類似。透過`self.offset `為`index`向`obj._slotvalues`取值。如果取回來的是預設的`sentinel`值`null`的話，表示該`index`值沒被正確指定又或者已經被刪除，`raise AttributeError`。最後，如果通過上述檢查的話，則將`obj._slotvalues[self.offset] `重設為`null`。
* `__repr__`中，指定`Member` `instance`的顯示格式。
```python=
null = object()

class Member:

    def __init__(self, name, clsname, offset):
        'Emulate PyMemberDef in Include/structmember.h'
        # Also see descr_new() in Objects/descrobject.c
        self.name = name
        self.clsname = clsname
        self.offset = offset

    def __get__(self, obj, objtype=None):
        'Emulate member_get() in Objects/descrobject.c'
        # Also see PyMember_GetOne() in Python/structmember.c
        if obj is None:
            return self
        value = obj._slotvalues[self.offset]
        if value is null:
            raise AttributeError(self.name)
        return value

    def __set__(self, obj, value):
        'Emulate member_set() in Objects/descrobject.c'
        obj._slotvalues[self.offset] = value

    def __delete__(self, obj):
        'Emulate member_delete() in Objects/descrobject.c'
        value = obj._slotvalues[self.offset]
        if value is null:
            raise AttributeError(self.name)
        obj._slotvalues[self.offset] = null

    def __repr__(self):
        'Emulate member_repr() in Objects/descrobject.c'
        return f'<Member {self.name!r} of {self.clsname!r}>'
```
### 2. Type
`Type`是一個繼承`type`的`metaclass`，目的是針對`slot_names`中所列出的名字，逐一建立相對的`Member` `instance`，並加入`mapping`中，最後呼叫`type.__new__`生成`cls`。此舉相當於以`slot_names`中的名字，建立
`class variable`，並將其值指為相對應的`Member` `instance`。


```python=
class Type(type):
    'Simulate how the type metaclass adds member objects for slots'

    def __new__(mcls, clsname, bases, mapping, **kwargs):
        'Emulate type_new() in Objects/typeobject.c'
        # type_new() calls PyTypeReady() which calls add_methods()
        slot_names = mapping.get('slot_names', [])
        for offset, name in enumerate(slot_names):
            mapping[name] = Member(name, clsname, offset)
        return type.__new__(mcls, clsname, bases, mapping, **kwargs)
```
### 3. Object
`Object` `class`的目的為被後續`class`繼承。
* `__new__`先利用`super().__new__(cls)`生成`instance`。接著看看`cls`是不是有`slot_names`，如果有的話就建立一個長度為`len(slot_names)`的`list`，並將`list`中每個值都預設為`null`。接著透過`object.__setattr__`將`list`設為名為`_slotvalues`的`instance variable`，並回傳`instance`。請注意此處`object.__setattr__`的使用實有其必要(`註2`)。
* `__setattr__`中會檢查`cls`中是否有`slot_names`。如果有的話，檢查其名字是否有在`cls.slot_names`中，如果不在的話`raise AttributeError`。如果通過檢查的話，則`delegate`給`super().__setattr__`。
* `__delattr__`的邏輯類似`__setattr__`。如果沒通過檢查的話`raise AttributeError`，有通過的話，則`delegate`給`super().__delattr__`。

```python=
class Object:
    'Simulate how object.__new__() allocates memory for __slots__'

    def __new__(cls, *args, **kwargs):
        'Emulate object_new() in Objects/typeobject.c'
        inst = super().__new__(cls)
        if hasattr(cls, 'slot_names'):
            empty_slots = [null] * len(cls.slot_names)
            object.__setattr__(inst, '_slotvalues', empty_slots)
        return inst

    def __setattr__(self, name, value):
        'Emulate _PyObject_GenericSetAttrWithDict() Objects/object.c'
        cls = type(self)
        if hasattr(cls, 'slot_names') and name not in cls.slot_names:
            raise AttributeError(
                f'{cls.__name__!r} object has no attribute {name!r}'
            )
        super().__setattr__(name, value)

    def __delattr__(self, name):
        'Emulate _PyObject_GenericSetAttrWithDict() Objects/object.c'
        cls = type(self)
        if hasattr(cls, 'slot_names') and name not in cls.slot_names:
            raise AttributeError(
                f'{cls.__name__!r} object has no attribute {name!r}'
            )
        super().__delattr__(name)
```
### 4. H(class)
`H` `class`，使用`Type`為其`metaclass`，並繼承`Object`。`slot_names`就相當於`__slots__`，我們可以將允許的`instance variable`名字放進`slot_names`這個`list`中。

```python=
class H(Object, metaclass=Type):
    'Instance variables stored in slots'

    slot_names = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y
```
可以觀察`H.__dict__`，`slot_names`及`x`與`y`都設定好了。
```python=
>>> from pprint import pp
>>> pp(dict(vars(H)))
{'__module__': '__main__',
 '__doc__': 'Instance variables stored in slots',
 'slot_names': ['x', 'y'],
 '__init__': <function H.__init__ at 0x7fb5d302f9d0>,
 'x': <Member 'x' of 'H'>,
 'y': <Member 'y' of 'H'>}
```
### 5. h(instance)
`instance` `h`可以正常使用，`slots`之值存於`instance.__dict__`中的`_slotvalues`。
```python=
>>> h = H(10, 20)
>>> vars(h)
{'_slotvalues': [10, 20]}
>>> h.x = 55
>>> vars(h)
{'_slotvalues': [55, 20]}
```
當使用不在`slot_names`的名字時，會`raise AttributeError`，類似於使用`__slots__`的效果。
```python=
>>> h.xz
Traceback (most recent call last):
    ...
AttributeError: 'H' object has no attribute 'xz'
```

## 以`__init_subclass__`改寫`__slots__`
`metaclass`的功能非常強大，對於是否一定要使用其來解決問題，我們會慎之又慎。使用`decorator`來裝飾`cls`常是避免使用`metaclass`的一個方法。自從Python3.6加入`__init_subclass__`後，更是大幅度降低需要實作`metaclass`的機會。

以下我們嘗試使用`__init_subclass__`的方法，來修改上述`__slots__`的實作。

### MyObject
`MyObject`繼承`Object`，並實作有`__init_subclass__`。

於`__init_subclass__`中:
* 先使用`super().__init_subclass__()`，確保`MRO`上的`class`如果有實作`__init_subclass__`的話，能確實被呼叫。
* 接著的步驟與在`Type.__new__`類似，只是我們這裡是在`class`生成後，才 `mutate` `class`。而`Type.__new__`是於生成`class`前，就將這些操作放在`mapping`。


```python=
# 01
...

class MyObject(Object):
    def __init_subclass__(cls):
        'Add member objects for slots'
        super().__init_subclass__()
        slot_names = cls.__dict__.get('slot_names', [])
        clsname = cls.__name__
        for offset, name in enumerate(slot_names):
            setattr(cls, name, Member(name, clsname, offset))
        return cls
```
### H(class)
此時`H` `class`只需要繼承`MyObject`，而不需要客製的`metaclass`。
```python=
# 01
...

class H(MyObject):
    'Instance variables stored in slots'

    slot_names = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y
```
可以觀察`H.__dict__`，`slot_names`及`x`與`y`也一樣可以正常設定。
```python=
>>> from pprint import pp
>>> pp(dict(vars(H)))
{'__module__': '__main__',
 '__doc__': 'Instance variables stored in slots',
 'slot_names': ['x', 'y'],
 '__init__': <function H.__init__ at 0x00000132D34D9300>,
 'x': <Member 'x' of 'H'>,
 'y': <Member 'y' of 'H'>}
```
### h(instance)
`instance` `h`一樣可以正常使用，`_slotvalues`也設定無誤。
```python=
>>> h = H(10, 20)
>>> vars(h)
{'_slotvalues': [10, 20]}
>>> h.x = 55
>>> vars(h)
{'_slotvalues': [55, 20]}
```
當使用不在`slot_names`的名字時，一樣會`raise AttributeError`。
```python=
>>> h.xz
Traceback (most recent call last):
    ...
AttributeError: 'H' object has no attribute 'xz'. Did you mean: 'x'?
```

## 備註
註1：可參考[Python docs](https://docs.python.org/3/reference/datamodel.html#creating-the-class-object)於此處的敘述。

註2：這邊不能使用`inst._slotvalues = empty_slots`或`setattr(inst, '_slotvalues', empty_slots)`，因為這兩種語法都相當於使用`instance`的`__setattr__`。而我們恰恰於`Object`實作有`__setattr__`，其會在檢查中`raise AttributeError`，因為`_slotvalues`的確不在`cls.slot_names`中。此外，也不能使用`super().__setattr__('_slotvalues', empty_slots)`，因為我們是在`__new__`中，這相當於`super(Object, cls).__setattr__('_slotvalues', empty_slots)`，並不是我們想要的行為。如果一定要使用`super()`的話，可以考慮`super(Object, inst).__setattr__('_slotvalues', empty_slots)`。但這麼一來有點繞來繞去的，直接使用`object.__setattr__`可能更簡單一點。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/06_desc_how_to/day19_pure_python)。