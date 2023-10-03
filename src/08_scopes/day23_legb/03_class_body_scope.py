# 03
fruit = 'Apple'


class Basket:
    fruit = 'Orange'
    partition1 = [fruit] * 3
    partition2 = [fruit for _ in range(3)]

    def get_fruit(self):
        return f'{fruit}'


basket = Basket()
print(basket.get_fruit())  # Apple
print(basket.fruit)  # Orange
print(Basket.partition1)  # ['Orange', 'Orange', 'Orange']
print(basket.partition2)  # ['Apple', 'Apple', 'Apple']
