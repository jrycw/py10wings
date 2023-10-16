# [Day25] 九翼 - Exception Groups與except* : 導讀PEP654 

## 九翼大綱
`Exception Groups`與`except*`是在Python3.11新增加的例外處理功能。一直以來都想好好搞懂，但...（下略三千字）。這次終於趁著鐵人賽的機會，靜下心來研究如何使用這個新功能，其及相關應用場景。

本翼的程式碼幾乎全取自`PEP654`及參考資料。我們特別推薦[`Or Chen`於EuroPython中的講解](https://www.youtube.com/watch?v=w2aSfeXVn8A)。其內容深入淺出，很快就能掌握基本原理。

本翼將使用`EG`來代稱`BaseExceptionGroup`與/或`ExceptionGroup`。

[[Day25]](https://ithelp.ithome.com.tw/articles/10317777)一起來閱讀`PEP654`。
[[Day26]](https://ithelp.ithome.com.tw/articles/10317778)了解`Exception Groups`與`except*`的相關應用。

## PEP654摘要
> This document proposes language extensions that allow programs to raise and handle multiple unrelated exceptions simultaneously:
    * A new standard exception type, the ExceptionGroup, which represents a group of unrelated exceptions being propagated together.
    * A new syntax except* for handling ExceptionGroups.

PEP654摘要裡說明，`ExceptionGroup` 的功用是可以「同時」收集「沒有相關」的`exception`，往後傳遞，並由`except*`語法來處理例外。

## PEP654動機
由於Python3.11前的例外處理機制是，一次最多只能處理一個例外。但是有些情況，我們希望能同時`raise`多個「沒有關係」的例外，這在沒有引進新語法的情況下很難做到。

文中舉了五個例子：
1. Concurrent errors
  Python的`asyncio.gather`是一般大家處理`concurrent`問題時，會呼叫的api。它提供了一個參數`return_exceptions`來協助例外處理，當其為`True`時，會返回一個`list`，裡面包含所有成功的結果及例外;當其為`False`時，當遇到第一個例外時就會馬上`raise`。但使用`asyncio.gather`無法同時處理多種例外，雖然有像`Trio`這樣的library[試著解決這些問題](https://peps.python.org/pep-0654/#programming-without-except)，但使用起來比較不便。
2. Multiple failures when retrying an operation
  假如一個操作被retry多次後失敗，我們會想知道其全部失敗的情況，而不是最後一個。
3. Multiple user callbacks fail
  假如一個操作有多個callback，我們會想知道其全部失敗的情況，而不是最後一個。
4. Multiple errors in a complex calculation
  收集所有錯誤的情況，將提供更多資訊給如`Hypothesis`這樣的library來整理歸類錯誤。
5. Errors in wrapper code
  當有錯誤發生在`__exit__`時，其會掩蓋於`with`區塊中發生的錯誤。
  
## PEP654原則
`EG`與`except*`並非想要全面取代`Exception`與`except`語法，只是希望多提供一個選擇給開發者。已存在的library，若決定改使用`EG`與`except*`語法，應視為`API-breaking change`。文件建議應該引入新的API呼叫邏輯，而不要直接修改既有的。

## BaseExceptionGroup與ExceptionGroup
為了解決上述問題，Python3.11引進兩個新的例外型態，`BaseExceptionGroup`與`Exception`。其中`BaseExceptionGroup`繼承`BaseException`，而`ExceptionGroup`同時繼承`BaseExceptionGroup`及`Exception`。從這邊可以觀察出`ExceptionGroup`除了是`BaseExceptionGroup`，也是我們熟悉的`Exception`。
```python=
class BaseExceptionGroup(BaseException): ... 
class ExceptionGroup(BaseExceptionGroup, Exception):
```   

`BaseExceptionGroup`與`Exception`的`signature`如下：
```python=
BaseExceptionGroup(message, exceptions) : ...
ExceptionGroup(message, exceptions) : ...
```
兩者都是接收兩個參數，`message`與`exceptions`。`message`為`str`型態，而`exceptions`是一個可以`nested`的`sequence`，也就是說`EG`可以包在另一個`EG`的`exceptions`內，例如`ExceptionGroup('issues', [ValueError('bad value'), TypeError('bad type')])`。
* `ExceptionGroup`只能包住`Exception`的`subclass`，其於生成前會先檢查是否所有的`exception`都是`Exception`的`instance`，如果不是的話，會`raise TypeError`。
* `BaseExceptionGroup`可以包住任何`BaseExceptionGroup`的`subclass`。其於生成前會先檢查如果所有的`exception`都是`ExceptionGroup`的`subclass`，則其會直接生成`ExceptionGroup`的`instance`。 
* `BaseExceptionGroup.subgroup(condition)`可以根據給定`condition`，生成符合條件的`EG`，如`# 01`所示。
```python=
# 01
import traceback

eg = ExceptionGroup(
    "one",
    [
        TypeError(1),
        ExceptionGroup(
            "two",
            [TypeError(2), ValueError(3)]
        ),
        ExceptionGroup(
            "three",
            [OSError(4)]
        )
    ]
)
if __name__ == '__main__':
    traceback.print_exception(eg)
    print('subgroup: ')
    type_errors = eg.subgroup(lambda e: isinstance(e, TypeError))
    traceback.print_exception(type_errors)
    ...
```
使用`traceback.print_exception`可以印出`EG`的樹狀結構。當使用了`subgroup`後，可以看出與`TypeError`有關的例外都被挑選出來，形成一個新的`ExceptionGroup`。
```
  | ExceptionGroup: one (3 sub-exceptions)
  +-+---------------- 1 ----------------
    | TypeError: 1
    +---------------- 2 ----------------
    | ExceptionGroup: two (2 sub-exceptions)
    +-+---------------- 1 ----------------
      | TypeError: 2
      +---------------- 2 ----------------
      | ValueError: 3
      +------------------------------------
    +---------------- 3 ----------------
    | ExceptionGroup: three (1 sub-exception)
    +-+---------------- 1 ----------------
      | OSError: 4
      +------------------------------------
subgroup: 
  | ExceptionGroup: one (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | TypeError: 1
    +---------------- 2 ----------------
    | ExceptionGroup: two (1 sub-exception)
    +-+---------------- 1 ----------------
      | TypeError: 2
      +------------------------------------
```
如果是使用`split`的話，則會將結果分為選中與跟沒選中兩個`EG`(但當兩邊有一邊是空的話，則會回傳`None`，不是空的`EG`)。
```python=
# 01 
    match, rest = eg.split(lambda e: isinstance(e, TypeError))
    print('match:')
    traceback.print_exception(match)
    print('rest:')
    traceback.print_exception(rest)
    ...
```
```
match:
  | ExceptionGroup: one (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | TypeError: 1
    +---------------- 2 ----------------
    | ExceptionGroup: two (1 sub-exception)
    +-+---------------- 1 ----------------
      | TypeError: 2
      +------------------------------------
rest:
  | ExceptionGroup: one (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | ExceptionGroup: two (1 sub-exception)
    +-+---------------- 1 ----------------
      | ValueError: 3
      +------------------------------------
    +---------------- 2 ----------------
    | ExceptionGroup: three (1 sub-exception)
    +-+---------------- 1 ----------------
      | OSError: 4
      +------------------------------------
```
`subgroup`與`split`除了可以接受`callable`外，也可以直接接受例外。
```python=
# 01
    ...
    type_errors2 = eg.subgroup(TypeError)
    match, rest = eg.split(TypeError)
```
或是包含於`tuple`內的多個例外。
```python=
# 01
    ...
    type_errors3 = eg.subgroup((TypeError,))
    match, rest = eg.split((TypeError,))
```

### Subclassing Exception Groups
與`Exception`一樣，我們可以透過繼承`EG`來客製化自己的`EG`。當然您可以選擇自己實作`subgroup`與`split`。但是文件建議實作`derive`，因為無論呼叫`subgroup`或`split`，`derive`都會被使用。
`# 02`中我們繼承了`ExceptionGroup`，建立了客製化的`MyExceptionGroup` `class`。
* 於`__new__`中，添加給`obj`一個`errcode` `attribute`。請注意文件中特別提到，必須使用`__new__`而不能使用`__init__`，因為`BaseExceptionGroup.__new__`需要知道我們接收的參數。
* 於`derive`中，回傳了`MyExceptionGroup`的`instance`。如果沒有`overwrite` `derive`的話，當回傳全都是`Exception`的`instance`時會回傳`ExceptionGroup`，否則回傳`BaseExceptionGroup`。
```python=
# 02
class MyExceptionGroup(ExceptionGroup):
    def __new__(cls, message, excs, errcode):
        obj = super().__new__(cls, message, excs)
        obj.errcode = errcode
        return obj

    def derive(self, excs):
        return MyExceptionGroup(self.message, excs, self.errcode)
```
### Handling Exception Groups
當想針對某些例外做一些處理時，文件中提到可以使用`subgroup`來做。
`# 03`中`log_and_ignore_ENOENT`除了提供適當的布林值回傳外，還偷偷在` if isinstance(err, OSError) and err.errno == ENOENT`的條件下，做了`log`，這相當於在使用`subgroup`時，順手添加了額外的功能。
```python=
# 03
def log_and_ignore_ENOENT(err):
    if isinstance(err, OSError) and err.errno == ENOENT:
        log(err)
        return False
    else:
        return True

try:
    . . .
except ExceptionGroup as eg:
    eg = eg.subgroup(log_and_ignore_ENOENT)
    if eg is not None:
        raise eg
```

文件中提供了一個[`leaf_generator`](https://peps.python.org/pep-0654/#handling-exception-groups)，可以得到`EG`的全部`trackback`。
```python=
# 04
def leaf_generator(exc, tbs=None):
    if tbs is None:
        tbs = []
    tbs.append(exc.__traceback__)
    if isinstance(exc, BaseExceptionGroup):
        for e in exc.exceptions:
            yield from leaf_generator(e, tbs)
    else:
        yield exc, tbs
    tbs.pop()
```
## except*
`try-except*`是新增可以處理`EG`的語法。
* `except* xxxError`是根據`xxxError`是否為`EG`的`subclass`來判斷是否符合。
* `except* xxxError as e`的`e`，一定會是`EG`而不是`Exception`。
* 每一個`except*`都可以被執行最多一次。換句話說，一個`EG`可以走訪多個`except*`。
* 而每一個`exception`只會：
    * 被其中一個`except*`處理。
    * 沒有被任何`except*`處理，最後被`reraise`。
* 在這樣的處理邏輯下，每一個`Exception`是根據不同的`except*`區塊來處理，而與`EG`內其它`Exception`無關。


`EG`在`try-except*`的過程中會不斷丟棄已經符合條件的`Exception`。其原理為，`EG`會利用`split`遞迴地進行`match`，而當最後若還有沒被處理的例外時，將會`reraise`剩餘的`EG`。

文件中舉了一個概念性的例子，我們將它寫為`# 05a`。
```python=
# 05a
import traceback


class SpamError(Exception): ...
class FooError(Exception): ...
class BarError(Exception): ...
class BazError(Exception): ...

eg = ExceptionGroup('msg', [FooError(1), FooError(2), BazError()])
try:
    raise eg
except* SpamError:
    ...
except* FooError as e:
    print('Handling FooError: ')
    traceback.print_exception(e)
except* (BarError, BazError) as e:
    print('Handling (BarError, BazError): ')
    traceback.print_exception(e)
```

其概念大致上如`# 05b`。
* 一開始有一個`EG`被`raise`，假設命名為`unhandled`。我們使用`unhandled.split(SpamError)`來確認`unhandled`中有沒有`SpamError`。由於`EG`中沒有`SpamError`，所以`match`其實是`None`，`rest`就是`unhandled`。我們將`unhandled`設為`rest`繼續往下。
* `unhandled.split(FooError)`確認`FooError`於`EG`中，此時`match`為`ExceptionGroup('msg', [FooError(1), FooError(2)])`，而`rest`為`ExceptionGroup('msg', [BazError()])`。我們將`e`及`sys.exc_info()`設為`match`，並將`unhandled`設為`rest`繼續往下。
* `unhandled.split((BarError, BazError))`確認`(BarError, BazError)`其中最少有一個例外在`EG`中，此時`match`為`ExceptionGroup('msg', [BazError()])`，而`rest`為`None`。我們將`e`及`sys.exc_info()`設為`match`，而`rest`因為是`None`，代表`EG`內的例外都已被處理，所以沒有例外需要`reraise`，程式順利結束。
```python=
# 05b
... # SpamError, FooError, FooError,BazError定義同`# 05a`
eg = ExceptionGroup('msg', [FooError(1), FooError(2), BazError()])
# try:
unhandled = eg

# except* SpamError:
match, rest = unhandled.split(SpamError)
print(f'{match=}, {rest=}')
unhandled = rest

# except* FooError as e:
match, rest = unhandled.split(FooError)
print(f'{match=}, {rest=}')
unhandled = rest

# except* (BarError, BazError) as e:
match, rest = unhandled.split((BarError, BazError))
print(f'{match=}, {rest=}')
```
```
match=None, rest=ExceptionGroup('msg', [FooError(1), FooError(2), BazError()])
match=ExceptionGroup('msg', [FooError(1), FooError(2)]), rest=ExceptionGroup('msg', [BazError()])
match=ExceptionGroup('msg', [BazError()]), rest=None
```
### Naked Exceptions
當於`try-except*`的`try`中，`raise`一個不是`EG`的`Excpetion`，稱作`naked exception`。
* 如果`except*`區塊中有符合的條件時，會將該`Exception`打包成為一個`EG`，並給予空的`message`。這樣也符合`as e`的`e`一定會是`EG`的原則，如`# 06a`。
```python=
# 06a
try:
    raise BlockingIOError
except* OSError as e:
    print(repr(e)) # ExceptionGroup('', [BlockingIOError()])
```
* 如果`except*`中沒有符合的條件時，則`raise Exception`，如`# 06b`。
```python=
# 06b
try:
    try:
        raise ValueError(12)
    except* TypeError as e:
        print('never')
except ValueError as e:
    print(f'caught ValueError: {e!r}') # caught ValueError: ValueError(12)
```

### `except*`只考慮`try`中的`EG`或`Exception`
`except*`只考慮`try`中的`EG`，至於在`except*`中再被`raise`的`EG`或`Exception`會直接`raise`，不會進到剩餘的`except*`。

`# 07a`中，我們於`except* ValueError`又`raise`了一個`two` `EG`。
```python=
# 07a
try:
    raise ExceptionGroup("one", [ValueError('a')])
except* ValueError:
    raise ExceptionGroup("two", [KeyError('x')])
except* KeyError:
    print('never')
```
從`traceback`可以確認，`two` `EG`並沒有被`except* KeyError`抓到。
```
  + Exception Group Traceback (most recent call last):
  |   File "<stdin>", line 3, in <module>
  |     raise ExceptionGroup("one", [ValueError('a')])
  | ExceptionGroup: one (1 sub-exception)
  +-+---------------- 1 ----------------
    | ValueError: a
    +------------------------------------

During handling of the above exception, another exception occurred:

  + Exception Group Traceback (most recent call last):
  |   File "<stdin>", line 5, in <module>
  |     raise ExceptionGroup("two", [KeyError('x')])
  | ExceptionGroup: two (1 sub-exception)
  +-+---------------- 1 ----------------
    | KeyError: 'x'
    +------------------------------------
```

`# 07b`中，我們於`except* TypeError`又`raise`了一個`ValueError(2)`。
```python=
# 07b
try:
    raise TypeError(1)
except* TypeError:
    raise ValueError(2) from None  # <- not caught in the next clause
except* ValueError:
    print('never')
```
從`traceback`可以確認，`ValueError(2)`也沒有被`except* ValueError`抓到。
```
Traceback (most recent call last):
  File "<stdin>", line 5, in <module>
    raise ValueError(2) from None  # <- not caught in the next clause
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: 2
```

### Chaining
#### `raise` `EG` in `except*`
於`except*`中`raise` `EG`，會有chaining的效果。這是一個有趣的行為，可能直接從文件示例來看，會比較容易了解。

`# 08a`於`except* ValueError`中又`raise`了一個`EG`。
```python=
# 08a
try:
    raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
except* ValueError:
    raise ExceptionGroup("two", [KeyError('x'), KeyError('y')])
```
觀察其`traceback`可以發現，於`two` `EG`中，也可以看到`one` `EG`中的`ValueError('a')`。至於`one` `EG`中的`TypeError('b')`因為沒有適當的`except*`處理，所以最終被`reraise`。
```
  | ExceptionGroup:  (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | Exception Group Traceback (most recent call last):
    |   File "<stdin>", line 3, in <module>
    |     raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
    | ExceptionGroup: one (1 sub-exception)
    +-+---------------- 1 ----------------
      | ValueError: a
      +------------------------------------
    | 
    | During handling of the above exception, another exception occurred:
    | 
    | Exception Group Traceback (most recent call last):
    |   File "<stdin>", line 5, in <module>
    |     raise ExceptionGroup("two", [KeyError('x'), KeyError('y')])
    | ExceptionGroup: two (2 sub-exceptions)
    +-+---------------- 1 ----------------
      | KeyError: 'x'
      +---------------- 2 ----------------
      | KeyError: 'y'
      +------------------------------------
    +---------------- 2 ----------------
    | Exception Group Traceback (most recent call last):
    |   File "<stdin>", line 3, in <module>
    |     raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
    | ExceptionGroup: one (1 sub-exception)
    +-+---------------- 1 ----------------
      | TypeError: b
      +------------------------------------
```
我們可以將`# 08a`改寫為`# 08b`來處理`TypeError`。
```python=
# 08b
try:
    raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
except* ValueError:
    raise ExceptionGroup("two", [KeyError('x'), KeyError('y')])
except* TypeError:
    ...
```
此時觀察`traceback`可以發現，`TypeError('b')`被`except* TypeError`處理後，就不會再`reraise`。
```
  + Exception Group Traceback (most recent call last):
  |   File "<stdin>", line 3, in <module>
  |     raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
  | ExceptionGroup: one (1 sub-exception)
  +-+---------------- 1 ----------------
    | ValueError: a
    +------------------------------------

During handling of the above exception, another exception occurred:

  + Exception Group Traceback (most recent call last):
  |   File "<stdin>", line 5, in <module>
  |     raise ExceptionGroup("two", [KeyError('x'), KeyError('y')])
  | ExceptionGroup: two (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | KeyError: 'x'
    +---------------- 2 ----------------
    | KeyError: 'y'
    +------------------------------------
```
#### `raise` `Exception` in `except*`
文件對此段的說明是：
> Raising a new instance of a naked exception does not cause this exception to be wrapped by an exception group. Rather, the exception is raised as is, and if it needs to be combined with other propagated exceptions, it becomes a direct child of the new exception group created for that:

而我們的理解是當於`except*`中`raise` `Exception`時，若其需要與其它`EG`合併的話，會生成新的`EG`，並將此`Exception`加入到最後。雖然與chaining不太一樣，但純看`trackback`的感覺卻很相似，所以我們決定將此段一起整理到這邊。

```python=
# 08c
try:
    raise ExceptionGroup("eg", [ValueError('a')])
except* ValueError:
    raise KeyError('x')
```

```
  | ExceptionGroup:  (1 sub-exception)
  +-+---------------- 1 ----------------
    | Exception Group Traceback (most recent call last):
    |   File "<stdin>", line 2, in <module>
    | ExceptionGroup: eg (1 sub-exception)
    +-+---------------- 1 ----------------
      | ValueError: a
      +------------------------------------
    |
    | During handling of the above exception, another exception occurred:
    |
    | Traceback (most recent call last):
    |   File "<stdin>", line 4, in <module>
    | KeyError: 'x'
    +------------------------------------
```
### Raising exceptions in an except* block
此段文件花了不少篇幅講解，但主要就是說明下面兩種例外處理方式，即`raise e`與`raise`其實是不一樣的。差別是當顯性地`raise e`時，其會有自己的`metadata`，
```python=
def foo():                           | def foo():
    try:                             |     try:
        1 / 0                        |         1 / 0
    except ZeroDivisionError as e:   |     except ZeroDivisionError:
        raise e                      |         raise
                                     |
foo()                                | foo()
                                     |
Traceback (most recent call last):   | Traceback (most recent call last):
  File "/Users/guido/a.py", line 7   |   File "/Users/guido/b.py", line 7
   foo()                             |     foo()
  File "/Users/guido/a.py", line 5   |   File "/Users/guido/b.py", line 3
   raise e                           |     1/0
  File "/Users/guido/a.py", line 3   | ZeroDivisionError: division by zero
   1/0                               |
ZeroDivisionError: division by zero  |
```
從`# 09`中可以看出`except* ValueError as e`的處理是顯性`raise e`，而`except* OSError as e`的處理是直接`raise`。
```python=
# 09
try:
    raise ExceptionGroup(
        "eg",
        [
            ValueError(1),
            TypeError(2),
            OSError(3),
            ExceptionGroup(
                "nested",
                [OSError(4), TypeError(5), ValueError(6)])
        ]
    )
except* ValueError as e:
    print(f'*ValueError: {e!r}')
    raise e
except* OSError as e:
    print(f'*OSError: {e!r}')
    raise
```
從`traceback`可以清楚看出：
* `except* ValueError as e`由於是顯性`raise e`，所以有自己的`metadata`，獨立了一個`EG`出來。
* 而`except* OSError as e`於`raise`前，也是一個獨立的`EG`(記得`as e`之後，`e`一定是`EG`嗎?)，但因其又重新`raise`，所以會與還沒有被處理過的`TypeError`合併，成為最後被`raise`的`EG`。
```
*ValueError: ExceptionGroup('eg', [ValueError(1), ExceptionGroup('nested', [ValueError(6)])])
*OSError: ExceptionGroup('eg', [OSError(3), ExceptionGroup('nested', [OSError(4)])])
  | ExceptionGroup:  (2 sub-exceptions)
  +-+---------------- 1 ----------------
    | Exception Group Traceback (most recent call last):
    |   File "stdin", line 16, in <module>   
    |     raise e
    |   File "stdin", line 3, in <module>    
    |     raise ExceptionGroup(
    | ExceptionGroup: eg (2 sub-exceptions)
    +-+---------------- 1 ----------------
      | ValueError: 1
      +---------------- 2 ----------------
      | ExceptionGroup: nested (1 sub-exception)
      +-+---------------- 1 ----------------
        | ValueError: 6
        +------------------------------------
    +---------------- 2 ----------------
    | Exception Group Traceback (most recent call last):
    |   File "stdin", line 3, in <module>    
    |     raise ExceptionGroup(
    | ExceptionGroup: eg (3 sub-exceptions)
    +-+---------------- 1 ----------------
      | TypeError: 2
      +---------------- 2 ----------------
      | OSError: 3
      +---------------- 3 ----------------
      | ExceptionGroup: nested (2 sub-exceptions)
      +-+---------------- 1 ----------------
        | OSError: 4
        +---------------- 2 ----------------
        | TypeError: 5
        +------------------------------------
```

### Caught Exception Objects
這一小段概念很直觀，我們直接看`# 10`。當直接對`except* TypeError as e`中的`e`進行操作時，並不會`mutate` `eg`。
``` python=
# 10
eg = ExceptionGroup("eg", [TypeError(12)])
eg.foo = 'foo'
try:
    raise eg
except* TypeError as e:
    e.foo = 'bar'
print(eg.foo)  # 'foo'
```
### 語法整理
不能於同一個`try`中，混合使用`except`及`except*`。
```python=1
try:
    ...
except ValueError:
    pass
except* CancelledError:  # <- SyntaxError:
    pass                 #    combining ``except`` and ``except*``
                         #    is prohibited
```
可以使用傳統的`except`直接補抓`ExceptionGroup`，但不能使用`except*`。
```python=
try:
    ...
except ExceptionGroup:  # <- This works
    pass

try:
    ...
except* ExceptionGroup:  # <- Runtime error
    pass

try:
    ...
except* (TypeError, ExceptionGroup):  # <- Runtime error
    pass
```
不能僅使用`except*`。
```python=
try:
    ...
except*:   # <- SyntaxError
    pass
```
有趣的是因為`ExceptionGroup`是繼承`Exception`而來，所以我們可以使用`except* Exception as ex`，此時`ex`一樣會是`EG`。
```python=
# 11
try:
    raise ExceptionGroup("one", [ValueError('a'), TypeError('b')])
except* Exception as ex:  # This works
    print(type(ex), ex) # <class 'ExceptionGroup'> one (2 sub-exceptions)
```
## 參考資料
* [PEP 654](https://peps.python.org/pep-0654/#naked-exceptions)。
* [Raise better errors with Exception Groups - presented by Or Chen](https://www.youtube.com/watch?v=w2aSfeXVn8A)。
* [Exception Groups and except: Irit Katriel](https://www.youtube.com/watch?v=uARIj9eAZcQ)。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/09_exceptiongroups/day25_exceptiongroups_pep654)。