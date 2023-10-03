# 00
async def coro1():
    raise ValueError('1')


async def coro2():
    raise TypeError('2')


async def coro3():
    raise TypeError('3')


async def coro4():
    return 'coro4 is good'
