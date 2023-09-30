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

    # def __iter__(self):
    #     """method 1"""
    #     return iter(self._cars)

    # def __iter__(self):
    #     """method 2"""
    #     return (car for car in self._cars)

    # def __iter__(self):
    #     """method 3"""
    #     for car in self._cars:
    #         yield car

    # def __iter__(self):
    #     """method 4"""
    #     yield from self._cars

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


if __name__ == '__main__':
    garage = Garage(['Koenigsegg Regera', 'Ford Mustang', 'Tesla Model X'])
    for car in garage:
        print(car)

    garage.add_car('Peugeot 308')
    for car in garage:
        print(car)  # Peugeot 308 now in garage

    garage_iter = iter(garage)
    print(next(garage_iter))  # Koenigsegg Regera
    print(next(garage_iter))  # Ford Mustang
    print(next(garage_iter))  # Tesla Model X
    print(next(garage_iter))  # Peugeot 308

    garage_iter._index = 0
    print(next(garage_iter))  # Koenigsegg Regera
