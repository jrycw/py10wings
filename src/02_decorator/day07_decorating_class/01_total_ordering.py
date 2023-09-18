# 01
from functools import total_ordering


@total_ordering
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.x, self.y) == (other.x, other.y)
        return NotImplemented


@total_ordering
class PointWithoutCustomEq:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return (self.x, self.y) < (other.x, other.y)
        return NotImplemented


if __name__ == '__main__':
    p1, p2 = Point(0, 0), Point(0, 0)
    print(p1 == p2)  # True

    p3, p4 = PointWithoutCustomEq(0, 0), PointWithoutCustomEq(0, 0)
    print(p3 == p4)  # False!!!
