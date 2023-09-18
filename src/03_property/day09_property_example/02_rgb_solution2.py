# 02
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
    def hex(self):
        if self._hex is None:
            self._hex = ''.join(f'{c:02x}' for c in self.color)
        return self._hex


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


if __name__ == '__main__':
    red, green, blue = Red(), Green(), Blue()
    print(f'{red.color=}, {red.hex=}')
    print(f'{green.color=}, {green.hex=}')
    print(f'{blue.color=}, {blue.hex=}')
