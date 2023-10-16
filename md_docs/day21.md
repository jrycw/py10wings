# [Day21] 七翼 - Protocols : Iteration Protocol

首先我們要先來聊聊`iterable`與`iterator`。

## iterable vs iterator
從`iterable`在[Python docs](https://docs.python.org/3/glossary.html#term-iterable)的說明：
> ... When an iterable object is passed as an argument to the built-in function iter(), it returns an iterator for the object. ... 

我們可以定義說，如果將`obj`傳遞給`iter`，能夠順利取得`iterator`而不`raise TypeError`的話，那麼該`obj`就是`iterable`。

那`iterator`又該怎麼定義呢? 從`iterator`在[Python docs](https://docs.python.org/3/glossary.html#term-iterator)的說明：
> ...  Repeated calls to the iterator’s `__next__()` method (or passing it to the built-in function next()) return successive items in the stream. When no more data are available a StopIteration exception is raised instead. At this point, the iterator object is exhausted and any further calls to its `__next__()` method just raise StopIteration again. Iterators are required to have an `__iter__()` method that returns the iterator object itself so every iterator is also iterable and may be used in most places where other iterables are accepted. ...
> 
我們可以總結：
* 能夠使用`next`或`obj`的`__next__`連續取值。
* 如果該`iterator`是有限的，那麼`iterator`耗盡後再呼叫`next`或`obj`的`__next__`，會`raise StopIteration`。
* `iterator`是一種`iterable`。當對`iterator`使用`iter`時，將取回其`iterator`本身。

如果滿足以上幾點的話，那麼該`obj`就是`iterator`。

## iteration protocol
iteration protocol會先看看`obj`是否有實作`__iter__`，如果有的話就嘗試是否能透過呼叫`__iter__`得到`iterator`，並利用`next`或`iterator`的`__next__`取值。如果沒有實作`__iter__`，卻滿足昨天的`Sequence protocol`時，會退一步使用`__getitem__`來取值。

## 如何生成iterator
如何生成`iterator`，我們提供以下五種方法。

### 方法1: 利用`iter`來得到其它`iterable`的`iterator`
我們可以直接使用`iter(obj)`來取得`obj`的`iterator`。

### 方法2: generator expression
`generator expression`的寫法與`list comprehensions`幾乎一樣，只是將`[]`改成`()`，其回傳型態是`generator`，可以視為一種`iterator`。

### 方法3: generator function by yield
於`function`中使用`yield`關鍵字，使得`function`成為一個`generator function`，其回傳型態也是`generator`。

### 方法4: generator function by yield from
於`function`中使用`yield from`關鍵字，使得`function`成為一個`generator function`，其回傳型態也是`generator`。

### 方法5: iterator class
`iterator class`即是參照`iterator`基本定義，建立一個`class`，並照其`protocol`實作`__iter__`及`__next__`。

## 實例

### 情境說明
假設您在一間新創公司辛苦打拼數年，最終如願IPO，於是決定將部份股份賣出，買下幾部心儀已久的車款。身為Python高手的您，決定寫個`Garage` `class`來管理這些車子，且`Garage`所生成的`instance`必須是個`iterable`，可以逐個顯示當前車庫內的車子。

### 實作細節
* 首先您建立了`Garage` `class`，裡面有一些基礎的功能來幫助管理。
```python=
# 01
from contextlib import suppress


class Garage:
    def __init__(self, cars=()):
        self._cars = list(cars)

    def __len__(self):
        return len(self._cars)

    def __getitem__(self, index):
        return self._cars[index]

    def add_car(self, car):
        self._cars.append(car)

    def remove_car(self, car):
        with suppress(ValueError):
            self._cars.remove(car)    
```
* 因為`Garage`符合`sequence protocol`，所以其生成的`instance`會是一個`iterable`。但身為Python高手的您知道，這樣是比較沒有效率的，於是您決定試著實作上述五種生成`iterator`的方式。

#### 方法1:
```python=
# 01
class Garage:
    ...
    def __iter__(self):
        """method 1"""
        return iter(self._cars)
```
`self._cars`是`list`型態，所以我們可以直接透過`iter`取得`list`的`iterator`回傳，其型態為`list_iterator`。

#### 方法2:
```python=
# 01
class Garage:
    ...
    def __iter__(self):
        """method 2"""
        return (car for car in self._cars)
```
`self._cars`是`iterable`，所以我們可以對其打個迴圈，使用`generator expression`產生一個`generator`。

#### 方法3:
```python=
# 01
class Garage:
    ...
    def __iter__(self):
        for car in self._cars:
            yield car
```
`self._cars`是`iterable`，所以我們可以對其打個迴圈，利用`yield`關鍵字產生一個`generator`。

#### 方法4:
```python=
# 01
class Garage:
    ...
    def __iter__(self):
        """method 4"""
        yield from self._cars
```
`self._cars`是`iterable`，所以我們可以利用`yield from`關鍵字產生一個`generator`。

#### 方法5:
```python=
# 01
class Garage:
    ...
    def __iter__(self):
        """method 5"""
        return GarageIterator(self)
    
    
class GarageIterator:
    def __init__(self, garage_obj):
        self._garage_obj = garage_obj
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._garage_obj):
            raise StopIteration
        car = self._garage_obj[self._index]
        self._index += 1
        return car
```
`方法5`我們於`__iter__`中回傳`GarageIterator`的`instance`，其接受一個參數`self`(即`Garage`所生成的`instance`)。

我們逐一比對`GarageIterator`所生成的`instance`，是否會符合我們對`iterator`的定義：
* 可以使用`obj`的`__next__`連續取值。
* 此`iterator`為有限的，當耗盡後若再呼叫`next`或`obj`的`__next__`，會`raise StopIteration`。
* 其`__iter__`會回傳`self`，即`GarageIterator`生成的`instance`。

發現全都符合，所以`GarageIterator` `class`是一個`iterator class`。

### 實際使用
`方法1~5`都能正常使用。
```python=
# 01
...
if __name__ == '__main__':
    garage = Garage(['Koenigsegg Regera', 'Ford Mustang', 'Tesla Model X'])
    for car in garage:
        print(car)
```
```
Koenigsegg Regera
Ford Mustang
Tesla Model X
```
且當我們使用`add_car`加入新車到車庫後，`__iter__`也很聰明的能夠反應現況。
```python=
# 01
...
if __name__ == '__main__':
    ... 
    garage.add_car('Peugeot 308')
    for car in garage:
        print(car)  # Peugeot 308 now in garage
```
```
Koenigsegg Regera
Ford Mustang
Tesla Model X
Peugeot 308
```

### 特別的方法5
`方法1~4`是我們一般常使用的方法。`方法5`雖然明顯麻煩不少，但是我們可以偷偷改變`iterator`的狀態。
```python=
# 01
...
if __name__ == '__main__':
    ... 
    garage_iter = iter(garage)
    print(next(garage_iter))  # Koenigsegg Regera
    print(next(garage_iter))  # Ford Mustang
    print(next(garage_iter))  # Tesla Model X
    print(next(garage_iter))  # Peugeot 308

    garage_iter._index = 0
    print(next(garage_iter))  # Koenigsegg Regera
```
上面的程式中，我們先使用`iter(garage)`將`GarageIterator`生成的`iterator`拿在手上。接下來呼叫四次`next`，分別取得`Koenigsegg Regera`、`Ford Mustang`、`Tesla Model X`及`Peugeot 308`。接著我們將`garage_iter._index`設為`0`，然後再次呼叫`next`，就又可以再次取得`Koenigsegg Regera`了。

除了可以改變`iterator`的狀態外，我們還可以在`GarageIterator`內加上其它`attribute`或`function`，這是`方法1~4`無法做到的。

## 當日筆記
當需要生成`iterator`時，我們應該優先使用`方法1~4`，因為這幾個方法都能快速生成`iterator`。但當我們需要在`iteration`過程中改變`iterator`狀態，或需要有特殊的`attribute`或`function`可以使用的話，就得依照`iterator`的基本定義，來實作像`方法5`的`iterator class`。

## 參考資料
* [Python Morsels - Iterator Protocol](https://www.pythonmorsels.com/iterator-protocol/)
* [Python Morsels - How to make an iterator in Python](https://www.pythonmorsels.com/how-to-make-an-iterator-in-python/)
* [Python for network engineers - VI. Basics of object-oriented programming - 23. Special methods - Protocols - Iteration protocol](https://pyneng.readthedocs.io/en/latest/book/23_oop_special_methods/iterable_iterator.html)

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/07_protocols/day21_iteration_protocol)。