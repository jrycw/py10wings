# [Day22] 七翼 - Protocols：Context Manager Protocol
[Context Manager](https://docs.python.org/3/library/stdtypes.html#context-manager-types)是一種可以讓我們使用`with`，於進出某段程式碼時，執行某些程式碼的功能。

## Context Manager Protocol
Context Manager Protocol要求需實作`__enter__`及`__exit__`兩個`dunder method`。
### `__enter__`
`__enter__`的`signature`如下：
```python=
__enter__()
```
`__enter__`不接受參數，其返回值將可以用`with`搭配`as`的語法取得，例如`with ctxmgr() as obj`。

### `__exit__`
`__exit__`的`signature`如下：
```python=
__exit__(exc_type, exc_val, exc_tb)
```
其接收三個參數：
* `exc_type`為例外的`class`。
* `exc_val`為例外的`obj`（或想成`exc_type`的`instance`）。
* `exc_tb`為一個`traceback` `obj`。

當`__exit__`回傳值為：
* `truthy`時（`bool(回傳值)`為`True`），會忽略例外。
* `falsey`時（`bool(回傳值)`為`False`），會正常報錯。由於當`function`沒有顯性設定回傳值時，會回傳`None`。而`None`是`falsey`，所以context manager預設情況為正常報錯。


## 基本型態
`Context Manager`一般有兩種型態：
* `型態1`是希望在進入時啟動資源，而在離開時關閉資源。常見的應用場景是開關檔案，建立`database client`、`ssh client`或`http client`等等。
* `型態2`是希望能在`context manager`下，「暫時」有些特別的行為。常見的應用場景是設定臨時的環境變數或是臨時的`sys.stdout`或`sys.stderr`。
  
### 型態1
`型態1`接收的參數，通常用來生成底層真正使用的`obj`。例如建立一個`PostgreSQL`的`connection`可能需要`host`、`port`、`database name`、`username`及`password`等等參數。

於`__enter__`中可以做一些`setup`，例如建立`connection`、進行`logging`等。至於返回值一般會返回`self`，因為這樣可以方便使用於`class`中的其它`function`，但依照使用情況的不同，有時候返回底層`obj`會更加方便。

於`__exit__`中可以做一些`cleanup`，例如關閉`connection`、進行`logging`等。此外，有可能需要處理遇到的例外，並決定返回`truthy`或`falsey`。


```python=
# 01 PSEUDO CODE!!!
class Object:
    def __init__(self, **kwargs): ...
    def start(self): ...
    def finish(self): ...


class MyContextManager:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def _make_obj(self, **kwargs):
        return Object(**kwargs)

    def setup(self):
        """set up something and possibly call self._obj.start() to do something"""
        self._obj = self._make_obj(**self._kwargs)
        self._obj.start()

    def cleanup(self):
        """Possibly call self._obj.finish() to do something and clean-up something"""
        self._obj.finish()

    def __enter__(self):
        self.setup()
        # can:
        # 1. return self
        # 2. return self._obj
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # may need to handle exceptions
        self.cleanup()
```

### 型態2
`型態2`通常只接收單個或少數參數，這些參數可以用來建構於`context manager`中「暫時」想要的行為。例如`redirect` `stdout`，或是暫時覆寫某些環境變數等。

於`__enter__`中，我們會先使用`getter`儲存當前的狀態，再使用`setter`實現想要的行為。至於返回值，要看當前應用的情況，即使不返回（即返回`None`）也是常見的情況。

 於`__exit__`中，我們再使用`setter`回復原先的狀態。一樣需視情況來處理遇到的例外，並決定返回`truthy`或`falsey`。

```python=
# 02 PSEUDO CODE!!!
class MyContextManager:
    def __init__(self, new_x):
        self._new_x = new_x
        self._x = 'x'

    def __enter__(self):
        self._old_x = self._x
        self._x = self._new_x
        # can:
        # 1. return self
        # 2. return self._new_x
        # 3. return None (implicitly)
        return self._new_x

    def __exit__(self, exc_type, exc_val, exc_tb):
        # may need to handle exceptions
        self._x = self._old_x  # back to original state
        del self._old_x  # delete unused variable
```


## 三種context manager類型
Context Manager可以分為`single use`、`reusable`及`reentrant`三種[類型](https://docs.python.org/3/library/contextlib.html#single-use-reusable-and-reentrant-context-managers)。

### single use
`single use`是最常用的類型。每次需要使用這類型的`context manager`都需重新建立，重複使用將會`raise RuntimeError`。建議的使用方法是，盡量使用`with MyContextManager as ctx_mgr`的語法，而不要將其先存在一個變數，例如`ctx_mgr = MyContextManager()`，然後再`with ctx_mgr`，來降低發生重複使用的機率。

### reentrant
`reentrant`是指在`with ctx`區塊內再產生一個以上的`with ctx`區塊。`redirect_stdout`與`redirect_stderr`即是此種類型，我們稍後會欣賞其源碼。

### reusable
`reusable`是排除有`reentrant`特性的`context manager`。其可以多次呼叫，但是如果將其當`reentrant`來使用時，會報錯或出現非預期的行為。

## `ContextDecorator` and `contextmanager`
### `ContextDecorator`
假如您有一個實作了`__enter__`及`__exit__`的`context manager`，那麼只要再繼承[ContextDecorator](https://docs.python.org/3/library/contextlib.html#contextlib.ContextDecorator)，這個`context manager`就能當作`decorator`使用。其源碼非常精簡，就像是附加一個`__call__`在`context manager`上。其功能是在被裝飾的`function`被呼叫時，會自動將該`function`包在`with`區塊內執行，就像是顯示使用`with`一樣，真是一個巧妙的設計呀。

```python=
class ContextDecorator(object):

    def _recreate_cm(self):
        return self

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwds):
            with self._recreate_cm():
                return func(*args, **kwds)
        return inner
```
### `contextmanager`
當使用[contextmanager](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)裝飾在一個`generator function`上時，此`generator function`將具有`context manager`的特性，且其也可以作為`decorator`使用（因為`contextmanager`內部實作有使用`ContextDecorator`）。

下面是Python文件的示例。
```python=
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwds):
    # Code to acquire resource, e.g.:
    resource = acquire_resource(*args, **kwds)
    try:
        yield resource
    finally:
        # Code to release resource, e.g.:
        release_resource(resource)
```
其中yield的`resource`就相當於是`__enter__`中回傳值，可以方便我們使用下方`with managed_resource as resource`的語法來取得`resource`。
```python=
with managed_resource(timeout=3600) as resource:
    # Resource is released at the end of this block,
    # even if code in the block raises an exception
```

## `redirect_stdout`與`redirect_stderr`源碼
`contextlib`內有不少實作了`context manager`的好用工具，我們一起來瞧瞧[redirect_stdout](https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stdout)與[redirect_stderr](https://docs.python.org/3/library/contextlib.html#contextlib.redirect_stderr)是怎麼實作的。

```python=
class redirect_stdout(_RedirectStream):
    _stream = "stdout"
    
class redirect_stderr(_RedirectStream):
    _stream = "stderr"
```
原來兩個都是繼承`_RedirectStream`而來，只是`_stream`這個`class variable`設的不同而已，讓我們再繼續追下去。
```python=
class _RedirectStream(AbstractContextManager):

    _stream = None

    def __init__(self, new_target):
        self._new_target = new_target
        # We use a list of old targets to make this CM re-entrant
        self._old_targets = []

    def __enter__(self):
        self._old_targets.append(getattr(sys, self._stream))
        setattr(sys, self._stream, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stream, self._old_targets.pop())
```
`_RedirectStream`於：
* `__init__`中，接收一個參數，為想要`redirect`的新目標。另外建立了一個`self._old_targets`的`list`來收集舊目標。
* `__enter__`中，將當前的`sys.stdout`或`sys.stderr`附加到`self._old_targets`後，返回`self._new_target`（不是`self`）。這麼一來，我們就可以在`as`的關鍵字後，得回`self._new_target`。
* `__enter__`中，將當前的`sys.stdout`或`sys.stderr`設為`self._old_targets`所`pop`出來的值。`list`的`pop`可以同時刪除最後一個元素並將其返回，用在此處可謂恰如其分。

`_RedirectStream`屬於我們的`型態2`，於`__enter__`中儲存當前狀態後，改變到新狀態，最後再於`__exit__`中恢復原來狀態。而且其註解也寫明其是`re-entrant`的，這也是為什麼我們需要`self._old_targets`幫忙來儲存一個以上的狀態。

## 參考資料
* [Python Morsels - Creating a context manager in Python](https://www.pythonmorsels.com/creating-a-context-manager/)。
* [Python for network engineers - VI. Basics of object-oriented programming - 23. Special methods - Protocols - Context Manager](https://pyneng.readthedocs.io/en/latest/book/23_oop_special_methods/context_manager.html)。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/07_protocols/day22_context_manager_protocol)。