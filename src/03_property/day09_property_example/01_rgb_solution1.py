# 01
class Color:
    def __init__(self, color):
        self.color = color
        self._hex = None

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

    @property
    def hex(self) -> str:
        if self._hex is None:
            self._hex = ''.join(f'{c:02x}' for c in self.color)
        return self._hex


class Red(Color):
    def __init__(self):
        super().__init__((255, 0, 0))

    @property
    def color(self):
        return super().color


if __name__ == '__main__':
    red = Red()  # AttributeError
