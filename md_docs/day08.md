## 三翼大綱
`property`實作有`__get__`、`__set__`及`__delete__`，所以是一種`data descriptor`。其具備有簡潔的語法能方便使用，而不用煩惱`descriptor`的實作細節。
* [[Day08]](https://ithelp.ithome.com.tw/articles/10317760)分享`property`核心原理及基本使用型態。
* [[Day09]](https://ithelp.ithome.com.tw/articles/10317761)舉一個實例，看看如何活用`property`。

## 核心原理
`property`的`signature`如下：
```python=
property(fget=None, fset=None, fdel=None, doc=None) -> property
```
可以將其想為一個`class`，並接受四個選擇性參數。以下我會以`prop`來稱呼由`property`建立的`property` `instance`。
* `fget`控制`instance.prop`時的行為。
* `fset`控制`instance.prop = value`時的行為。
* `fdel`控制`del instance.prop`時的行為。
* `doc`為`prop`的說明文件。如果沒有指定`doc`，而`prop`裡有`fget`時，會將`doc`設為`fget`中的`__doc__`。
* 每當我們建立`prop`後，想要新增`fget`、`fset`或`fdel`時，我們不`mutate` `prop`，而是透過`property.getter`、`property.setter`或`property.deleter`來新建一個`prop`返回。

## 基本型態
`# 01`為`property`的基本型態。
```python=
# 01
class MyClass:
    def __init__(self, x):
        self.x = x

    @property
    def x(self):
        """docstrings from fget"""
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        del self._x


if __name__ == '__main__':
    my_inst = MyClass(1)
```
* 首先我們將`property`裝飾於`function` `x`上，而此`function` `x`內具有當使用`my_inst.x`語法時的行為。此裝飾相當於`x = property(x)`:
    * 將`function` `x`作為`property`的第一個參數`fget`，並返回`prop`，且命名為`x`。
    * 現在的`prop` `x`內已有`fget`及`doc`，但還未有`fset`及`fdel`。

* 接著將`x.setter`裝飾於另一個`function` `x`上，而此`function` `x`內具有當使用`my_inst.x = value`語法時的行為。此裝飾相當於`x = x.setter(x)`:
    * `prop` `x`的`setter`接收這個`function` `x`。
    * 於`setter`中，將會生成一個新的`prop`，以第一步的`fget`作為`fget`及`doc`作為`doc`，再加上剛剛接收的`function` `x`作為`fset`。
    * 最後返回此新`prop`，且命名為`x`。現在的`prop` `x`內已有`fget`、`fset`及`doc`，但還未有`fdel`。

* 最後將`x.deleter`裝飾於另一個`function` `x`上，而此`function` `x`內具有當使用`del my_inst.x`語法時的行為。此裝飾相當於`x = x.deleter(x)`:
    *  `prop` `x`的`deleter`接收這個`function` `x`。
    * 於`deleter`中，將會生成一個新的`prop`，以上一步的`fget`作為`fget`、`doc`作為`doc`及`fset`作為`fset`，再加上剛剛接收的`function` `x`作為`fdel`。
    * 最後返回此新`prop`，且命名為`x`。現在的`prop` `x`內已完整擁有`fget`、`fset`、`fdel`及`doc`。

* 乍看之下，`# 01`只是生成了`my_inst`，還沒有任何與`prop` `x`互動。但仔細看看`__init__`，`my_inst`已經透過`property`這個介面呼叫了`prop` `x`的`fset`來進行`self.x = x`(`self`就是`my_inst`啊)。

* `@x.setter`與`@x.deleter`裝飾的`function`必須與`@property`所裝飾的`function`名一致，即`x`。如果使用不同名字，使用上會變得很困難，且容易出錯(`註1`)。

`# 01`是基本型態，但視您的程式需要，您可能需要先建立一個`prop`，然後再視情況加入`fget`、`fset`、`fdel`或`doc`，如`# 01a`。
```python=
# 01a
class MyClass:
    def __init__(self, x):
        self.x = x

    prop = property()

    @prop.getter
    def x(self):
        """docstrings from fget"""
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

    @x.deleter
    def x(self):
        del self._x
```
又或者您可以建立好`fget`、`fset`、`fdel`或`doc`，再一次生成`prop`，如`# 01b`。
```python=
# 01b
class MyClass:
    def __init__(self, x):
        self.x = x

    def get_x(self):
        return self._x

    def set_x(self, value):
        self._x = value

    def del_x(self):
        del self._x

    x = property(fget=get_x,
                 fset=set_x,
                 fdel=del_x,
                 doc="""docstrings""")
```


## `property`適用時機
* 當您於`instance`中有一個變數，不想直接被存取，而希望使用者透過給定的接口(`getter`、`setter`與`deleter`)來操作這個變數。由於使用`property`來存取變數，與存取一般變數的語法是相同的，所以我們寫`code`時，可以不用一開始就決定哪些變數要使用`property`，等到`code`的中後段再來判斷，而所有的`interface`並不需要因此修改。
* 當一個變數值是需要動態計算而得，一般會實作一個`function`。但有些時候，這個變數更像是`instance attribute`，並且大多會使用快取的機制時，也是一個適合使用`property`的時機。


## 備註
註1：
* `@x.setter`相當於`set_x = x.setter(set_x)`，意思是使用`prop` `x`的`fget`及`doc`加上現在的`set_x`建立一個新`prop`返回，並命名為`set_x`。現在`MyClass`有兩個`prop`：
    * 第一個是`prop` `x`，擁有`fget`及`doc`。
    * 第二個是`prop` `set_x`，擁有`fget`、`fset`及`doc`。

* `@x.deleter`相當於`del_x = x.deleter(del_x)`，意思是使用`prop` `x`的`fget`及`doc`加上現在的`del_x`建立一個新`prop`返回，並命名為`del_x`。現在`MyClass`有三個`prop`：
    * 第一個是`prop` `x`，擁有`fget`及`doc`。
    * 第二個是`prop` `set_x`，擁有`fget`、`fset`及`doc`。
    * 第三個是`prop` `del_x`，擁有`fget`、`fdel`及`doc`。
* 僅管我們還是可以使用`my_inst.x`的語法，但：
    * `my_inst.x = value`必須改成`my_inst.set_x = value`。
    * `del my_inst.x`必須改成`del my_inst.delx`。
```python=
# 101
class MyClass:
    def __init__(self, x):
        self.set_x = x  # not self.x = x

    @property
    def x(self):
        """docstrings from fget"""
        return self._x

    @x.setter
    def set_x(self, value):
        self._x = value

    @x.deleter
    def del_x(self):
        del self._x


if __name__ == '__main__':
    my_inst = MyClass(1)
    for name, prop in (('x', MyClass.x),
                       ('set_x', MyClass.set_x),
                       ('del_x', MyClass.del_x)):
        print(f'prop {name=}: ')
        print(f'type of prop {name} is {type(prop)}')
        print(f'fget={prop.fget}')
        print(f'fset={prop.fset}')
        print(f'fdel={prop.fdel}')
        print(f'doc={prop.__doc__}\n')
```
```
prop name='x': 
type of prop x is <class 'property'>
fget=<function MyClass.x at 0x00000142E5AC4EA0>
fset=None
fdel=None
doc=docstrings from fget

prop name='set_x': 
type of prop set_x is <class 'property'>
fget=<function MyClass.x at 0x00000142E5AC4EA0>
fset=<function MyClass.set_x at 0x00000142E5AC4E00>
fdel=None
doc=docstrings from fget

prop name='del_x':
type of prop del_x is <class 'property'>
fget=<function MyClass.x at 0x00000142E5AC4EA0>
fset=None
fdel=<function MyClass.del_x at 0x00000142E5AC6340>
doc=docstrings from fget
```

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/03_property/day08_property)。