# [Day09] 三翼 - property：實例說明

今日我們透過解題，來練習看看如何活用`property`。以下會以`prop`來稱呼由`property`建立的`property` `instance`。

## 問題
1. 建立一個`Color` `class`：
    * 接受一個參數`color`，其為一代表`(r, g, b)`格式的`tuple`。
    * 實作一個名為`color`的`prop` ，具有`getter`及`setter`功能。
    * 實作一個名為`hex`的`prop`，可動態計算`prop` `color`的`Hex color code`，並具備快取機制。
2. 建立一個`class` `Red`繼承`Color`：
    * 實作一個名為`color`的`prop` ，其只有`getter`功能，而沒有`setter`功能。

### 解法1
首先定義`Color` `class`，並實作`__init__`。
* `self.color = color`暗示其會呼叫`color` `prop`的`setter`，來幫忙設定`color`。
* `self._hex`為`hex` `prop`底下真正包含的值，先於此定義。
```python=
# 01
class Color:
    def __init__(self, color):
        self.color = color
        self._hex = None
```
接著實作`color` `prop`的`getter`及`setter`。
* `getter`會返回`self._color`這個`color` `prop`底下真正包含的值。
* `setter`會先呼叫`_validate`做兩個檢查，確保給定的`color`值為`tuple`型態且`tuple`中每個元素都是範圍在`0~255`之間的`int`。如果通過的話，則將給定的`color`指定給`self._color`，並將`self._hex`設為`None`。`self._hex = None`相當於每次呼叫`color`的`setter`時會清除`hex` `prop`的快取機制。
```python=
# 01
class Color:
    ...
    
    def _validate(self, color):
        if not isinstance(color, tuple):
            raise ValueError('color value must be a tuple')
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            raise ValueError(
                'color value must be an integer and 0 <= color value <=255')

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._validate(color)
        self._color = color
        self._hex = None  # purge cache
```
再來實作`hex` `prop`。先確認`self._hex`是否為`None`，若是的話代表第一次呼叫或是快取已被清除，此時需真正計算`Hex color code`，最後再返回`self._hex`。請注意我們使用`self.color`來存取`self._color`，而非直接使用`self._color`。雖然兩種方式都可以，但是當有`property`這種公開的`interface`時，建議優先使用。因為這麼一來當`interface`有問題時，身為第一個使用者的我們很容易發現。
```python=
# 01
class Color:
    ...
    
    @property
    def hex(self):
        if self._hex is None:
            self._hex = ''.join(f'{c:02x}' for c in self.color)
        return self._hex
```
最後實作`Red` `class`。因為我們很明確知道紅色的`color`為`(255, 0, 0)`，所以可以直接在`__init__`中利用`super()`來請`Color` `class`來幫忙設定。
```python=
# 01
class Red(Color):
    def __init__(self):
        super().__init__((255, 0, 0))
```
但是這麼寫有個問題是，我們可以使用`color` `prop`的`setter`來直接指定`color`，像是下面這樣就變成「紅皮綠底」了啊。
```python=
>>> red = Red()
>>> red.color = (0, 255, 0) # green 
```
一個解決的方法是，於`Red`中實作自己的`color` `prop`。
```python=
class Red(Color):
    ...
    
    @property
    def color(self):
        return self.color
```
可是這麼寫也不行呀，`self.color`會不斷再呼叫`self.color`直到報錯。此時我們真正需要的是當呼叫`self.color`時，利用`super()`將呼叫`delegate`回`Color`，所以應該寫為：
```python=
class Red(Color):
    ...
    
    @property
    def color(self):
        return super().color
```
至此我們完成`Red` `class`的實作。但當試圖建立`red`時，卻發現會`raise AttributeError`，這是怎麼一回事呢？
```python=
>>> red = Red() # AttributeError: property 'color' of 'Red' object has no setter
```
原來是因為我們在`Red`中已經`overwrite`了`color` `prop`，其只有具備`getter`功能。而在`Red`的`__init__`將呼叫`delegate`回`Color`的`__init__`時，其中的`self.color = color`會需要呼叫`color` `prop`的`setter`。

請注意這邊有一個在使用`property`時常見的誤解。有些朋友可能會覺得我們於`Red`中只`overwrite`了`color`的`getter`，但是沒有`overwrite`的`color`的`setter`，所以不應該報錯呀？

這個誤解的來源是將`getter`與`setter`分別視為了兩個`prop`。但是正確的思路是，`Color` `class`其內的`color` `prop`同時實作有`fget`及`fset`，而`Red` `class`其內的`color` `prop`只有實作`fget`。而當我們由`red`來呼叫`color`時，`self`相當於`red`，而`self.color = color`相當於`red.color = color`，由於該`prop`沒有實作`fset`，所以會報錯。

我們將於`解法2`解決這個問題。

### 解法2
我們將原先`color` `prop`中`setter`的邏輯，移到新的`_set_color` `function` 中。並將`Color.__init__`中的`self.color = color`改為`self._set_color(color)`。這麼一來就能符合題意，巧妙的解決問題。

```python=
# 02
class Color:
    def __init__(self, color):
        self._set_color(color)
        self._hex = None

    def _validate(self, color):
        if not isinstance(color, tuple):
            raise ValueError('color value must be a tuple')
        if not all(isinstance(c, int) and 0 <= c <= 255 for c in color):
            raise ValueError(
                'color value must be an integer and 0 <= color value <=255')

    def _set_color(self, color):
        self._validate(color)
        self._color = color
        self._hex = None  # purge cache

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._set_color(color)

    @property
    def hex(self):
        if self._hex is None:
            self._hex = ''.join(f'{c:02x}' for c in self.color)
        return self._hex
```
此外，可以善用`Enum`來幫助我們枚舉各種顏色，假設我們現在需要建立`Red`、`Green`及`Blue`三個`class`時，可以這麼寫：
```python=
# 02
from enum import Enum
...

class MyColor(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


class Red(Color):
    def __init__(self):
        super().__init__(MyColor.RED.value)

    @property
    def color(self):
        return super().color


class Green(Color):
    def __init__(self):
        super().__init__(MyColor.GREEN.value)

    @property
    def color(self):
        return super().color


class Blue(Color):
    def __init__(self):
        super().__init__(MyColor.BLUE.value)

    @property
    def color(self):
        return super().color
```
### 解法3
由於`解法2`裡我們於繼承`Color`的`class`內都要實作`color` `prop`，我們開始思考是不是能把這個`prop`抽象出來。

我們嘗試建立一個`ReadColorOnly` `class`來包住這個`prop`。這麼一來後續的`class`繼承`ReadColorOnly`及`Color`後，只需要實作`__init__`即可。

如果只需要建立`Red`、`Green`及`Blue`三個`class`時，我們會傾向`解法2`。但如果後續有很多像`LuckyColor`的`class`需要建立時，或許`解法3`會是比較好的選擇。

```python=
# 03
import random
...

class ReadColorOnly:
    @property
    def color(self):
        return super().color


class Red(ReadColorOnly, Color):
    def __init__(self):
        super().__init__(MyColor.RED.value)


class Green(ReadColorOnly, Color):
    def __init__(self):
        super().__init__(MyColor.GREEN.value)


class Blue(ReadColorOnly, Color):
    def __init__(self):
        super().__init__(MyColor.BLUE.value)


class LuckyColor(ReadColorOnly, Color):
    def __init__(self):
        super().__init__(tuple(random.choices(range(256), k=3)))
```

## 參考資料
本日內容啟發自[python-deepdive-Part 4-Section 06-Single Inheritance-Delegating to Parent](https://github.com/fbaptiste/python-deepdive/blob/main/Part%204/Section%2006%20-%20Single%20Inheritance/05%20-%20Delegating%20to%20Parent.ipynb)。

## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/03_property/day09_property_example)。