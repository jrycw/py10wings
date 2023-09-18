# 03
import random
from enum import Enum


class MyColor(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)


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
    def hex(self) -> str:
        if self._hex is None:
            self._hex = ''.join(f'{c:02x}' for c in self.color)
        return self._hex


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


if __name__ == '__main__':
    red, green, blue, lucky_color = Red(), Green(), Blue(), LuckyColor()
    print(f'{red.color=}, {red.hex=}')
    print(f'{green.color=}, {green.hex=}')
    print(f'{blue.color=}, {blue.hex=}')
    print(f'{lucky_color.color=}, {lucky_color.hex=}')

    c = Color(MyColor.RED.value)
    print(c.color, c.hex)
    c.color = tuple(random.randint(0, 255) for _ in range(3))
    print(c.color, c.hex)
