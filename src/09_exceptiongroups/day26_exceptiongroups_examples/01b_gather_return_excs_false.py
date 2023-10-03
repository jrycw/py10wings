# 01b
import asyncio


async def coro1():
    raise ValueError('1')


async def coro2():
    raise TypeError('2')


async def coro3():
    raise TypeError('3')


async def coro4():
    return 'coro4 is good'


async def main():
    tasks = []
    coros = [coro1(), coro2(), coro3(), coro4()]
    for coro in coros:
        task = asyncio.create_task(coro)
        tasks.append(task)

    # raise ValueError('1')
    await asyncio.gather(*tasks, return_exceptions=False)


if __name__ == '__main__':
    asyncio.run(main())
