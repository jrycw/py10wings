# 03b
import asyncio


async def coro1():
    raise ValueError('1')


async def coro2():
    raise TypeError('2')


async def coro3():
    raise TypeError('3')


async def coro4():
    return 'coro4 is good'


async def do_some_stuff():
    coros = [coro1(), coro2(), coro3(), coro4()]
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for coro in coros:
            task = tg.create_task(coro)
            tasks.append(task)


async def main():
    try:
        await do_some_stuff()
    except* Exception as eg:
        for exc in eg.exceptions:
            print(f'handling {exc}')


if __name__ == '__main__':
    asyncio.run(main())
