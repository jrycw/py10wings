# [Day03] 初翼 - Tips : 6~10
今天我們繼續分享`tips 6~10`。

## 6. 當function回傳值為bool
有時候，我們會寫一些輔助的`function`來判斷傳入值是否符合某些條件，符合回傳`True`，不符合回傳`False`。

* 一般我們會寫出像`# 06a`的模式，利用`if-else`來實作。
```python=
# 06a
def get_bool(iterable):
    if len(iterable) > 10:
        return True
    else:
        return False


if __name__ == '__main__':
    print(get_bool(range(10)), get_bool(range(11)))    # False, True
```
* 但仔細看看，`else`的部份，其實可以省略，所以也可以寫成`# 06b`的模式。
```python=
# 06b
def get_bool(iterable):
    if len(iterable) > 10:
        return True
    return False


if __name__ == '__main__':
    print(get_bool(range(10)), get_bool(range(11)))    # False, True
```
* 但`len(iterable) > 10`本身就會回傳`True`或是`False`，可以直接返回。所以就有了`# 06c`的模式。我們覺得`# 06c`這種模式俗又有力，推薦您使用。
```python=
# 06c
def get_bool(iterable):
    return len(iterable) > 10


if __name__ == '__main__':
    print(get_bool(range(10)), get_bool(range(11)))    # False, True
```
## 7. print to file
當我們有一個內含多個`str`的`list`要寫入檔案，且每個`str`需要自己獨立一行。
* 一般會寫出`# 07a`中的模式，手動於每次寫入時，加入`\n`。
```python=
# 07a
text = ['abcde', '12345']

with open('file1.txt', 'w') as f:
    for s in text:
        f.write(s+'\n')
```

* 由於`print`接受一個`file`參數，預設是`sys.stdout`，我們可以偷龍轉鳳將`open`之後的`f`指定給`file`，讓`print`來幫我們自動加入`\n`，如`# 07b`所示。

```python=
# 07b
text = ['abcde', '12345']

with open('file2.txt', 'w') as f:
    for s in text:
        print(s, file=f)
```
* 又由於`print`可以接受多個參數，所以我們可以進一步改寫`# 07b`為`# 07c`，直接傳入`*text`，並指定`sep='\n'`來節省一個迴圈。`# 07c`的寫法善用`built-in function`，且相當pythonic，推薦給您。

```python=
# 07c
text = ['abcde', '12345']

with open('file3.txt', 'w') as f:
    print(*text, sep='\n', file=f)
```
最後我們做個檢查。`# 07d`中[可以使用()將context manager分成多行的語法](https://docs.python.org/3.10/whatsnew/3.10.html#parenthesized-context-managers)，為Python 3.10新添增的。一般而言，`context manager`的命名會偏長，有了這個語法幫忙後，`code`看起來會清楚不少。
```python=
# 07d
with (open('file1.txt') as f1,
      open('file2.txt') as f2,
      open('file3.txt') as f3):
    print(f1.read() == f2.read() == f3.read())  # True
```

## 8. list unpacking
當有一個`list`包含一個`tuple`時，如`[('d', 4)]`的情況，該如何取得`'d'`及`4`呢？

一般的解法是先利用`[('d', 4)][0]`來拿到內層的`('d', 4)`，然後使用`d, four = ('d', 4)`的`tuple unpacking`，如`# 08a`。

```python=
# 08a
from collections import Counter

iterable = 'a'*1 + 'b'*2 + 'c'*3 + 'd'*4
cnter = Counter(iterable)
# cnter.most_common(1)  # [('d', 4)]

if __name__ == '__main__':
    # tuple unpacking
    d, four = cnter.most_common(1)[0]
    print(f'{d=}, {four=}')  # d='d', four=4
```

針對這種情況，我們會推薦使用`list unpacking` `[(d, four)] = [('d', 4)]`，如`# 08b`。沒錯，`[]`也能放在等號的左側。於此處使用`list unpacking`的好處是可以免去最外層需使用`list`來`indexing`，且擁有類似像`Rust`的語法，可以驗證左右側整體型式是否相同(`list`包含一個`tuple`，且`tuple`內元素數量要左右相同)。
```python=
# 08b
from collections import Counter

iterable = 'a'*1 + 'b'*2 + 'c'*3 + 'd'*4
cnter = Counter(iterable)
# cnter.most_common(1)  # [('d', 4)]

if __name__ == '__main__':
    # list unpacking
    [(d, four)] = cnter.most_common(1)
    print(f'{d=}, {four=}')  # d='d', four=4
```

此外`list unpacking`也支援像`tuple unpacking`一樣的`*`語法，如`# 08c`，來收集剩餘的元素。
```python=
# 08c
from collections import Counter

iterable = 'a'*1 + 'b'*2 + 'c'*3 + 'd'*4
cnter = Counter(iterable)
# cnter.most_common(1)  # [('d', 4)]

if __name__ == '__main__':
    # `*` can be used in list unpacking as well
    [(a, *_)] = [('a', 'b', 'c')]
    print(f'{a=}, {_=}')  # a='a', _=['b', 'c']
```

`list unpacking`雖然少見，但在這種特別的情形，我們會推薦使用。畢竟因為比較少用的關係，當自己在讀`code`看到時，很容易會注意到，反而會格外留心檢查右側的整體型別，或許這也是件好事吧XD


## 9. zip與dict的搭配使用
一般大家會使用`zip`的情況，應該是需要對多個`iterable`打迴圈的時候才會用到，但我們發現`zip`搭配`dict`也有許多妙用。

當需要一個`dict`，其`keys`為`a~z`，而`values`為`1~26`，您會如何建立呢（`註1`）？
一般來說，您應該會利用`dict-comprehension`，如`# 09a`。
```python=
# 09a
from string import ascii_lowercase

if __name__ == '__main__':
    # [str, int]
    d = {k: v
         for k, v in zip(ascii_lowercase, range(1, 27))}
```
但我們發覺`# 09b`這種寫法更加優雅。`zip`幫我們將`ascii_lowercase`與`count(1)`縫在一起，然後交給`dict`幫忙生成。短短一行，我們靈活地使用了`zip`與`itertools.count`。

`zip`的強大，不只在於縫製`iterable`，也可以體現於拆`iterable`。當您有一個`dict`，您會如何同時取得`keys`及`values`呢？
* 一般來說，您應該會使用`dict.keys()`與`dict.values()`。
* `keys, values = zip(*d.items())`是一種拆掉`d`的方法。這個方法得到的`keys`與`values`是`tuple`型態，所以可以使用`[]`來取值。而`dict.keys()`得到的`dict_keys`型態與`dict.values()`得到的`dict_values`型態，皆無法使用`[]`。
```python=
# 09b
from itertools import count
from string import ascii_lowercase

if __name__ == '__main__':
    # [str, int]
    d = dict(zip(ascii_lowercase, count(1)))
    keys, values = zip(*d.items())
```


## 10. 利用`continue`減少縮排
[continue](https://docs.python.org/3/reference/simple_stmts.html#continue)是一個於迴圈中離開當下這個`cycle`，進入下一個`cycle`的語法。

假設我們想要寫一個`my_filter` `function`（`註2`），其要求如下：

* 接受兩個參數`func`及`iterable`。`func`會針對`iterable`中每個`element`給出`True`或`False`
* 最後`my_filter`會以`generator`型式返回`func`判斷為`True`的元素。

一般來說，我們會寫出如`# 10a`的模式。但此時我們由於`for`與`if`，程式的主邏輯`yield item`得出現於第三層。如果外面層數過多，例如有使用`context manager`、多個迴圈或多個`if`，整體程式碼會很難閱讀。
```python=
# 10a
def func(x):
    try:
        return x > 10
    except TypeError:
        return False


def my_filter(func, iterable):
    """`yield item` locates at the second level of indentation"""
    for item in iterable:
        if func(item):
            yield item


if __name__ == '__main__':
    flt = my_filter(func, [2, 11, 'str', (), []])
    print(list(flt))  # [11]
```
如果我們搭配`not`與`continue`，則會寫出`# 10b`的模式。這麼一來我們就只縮排了`for`這一層，程式的主邏輯`yield item`可以出現於第二層。
```python=
# 10b
def func(x):
    try:
        return x > 10
    except TypeError:
        return False


def my_filter(func, iterable):
    """`yield item` locates at the first level of indentation
        by using `continue` to save one level of indentation"""
    for item in iterable:
        if not func(item):
            continue
        yield item


if __name__ == '__main__':
    flt = my_filter(func, [2, 11, 'str', (), []])
    print(list(flt))  # [11]
```

`# 10a`的方式較為直觀，但如若程式碼已縮排多層又很難重構的話，可以嘗試採用`# 10b`的寫法。


## 備註
註1：如果想要反過來，建立一個`keys`為`1~26`，`values`為`a-z`的`dict`，可以這麼做：
```python=
# 09c
from string import ascii_lowercase

if __name__ == '__main__':
    # [int, str]
    d = dict(enumerate(ascii_lowercase, 1))
```

註2：[Python的`filter`](https://docs.python.org/3/library/functions.html#filter)實作大致如下，我們實作的是個閹割的版本。
```python=
# 10c
def my_filter(func, iterable):
    """Emulate built-in filter"""
    if func is not None:
        return (item for item in iterable if func(item))
    return (item for item in iterable if item)
```

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/01_tips/day03_tips_6_10)。