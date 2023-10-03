# 03a
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
    coros = [coro1(), coro2(), coro3(), coro4()]
    tasks = []
    try:
        async with asyncio.TaskGroup() as tg:
            for coro in coros:
                task = tg.create_task(coro)
                tasks.append(task)
    except* Exception as eg:
        for exc in eg.exceptions:
            print(f'handling {exc}')
    else:
        for task in tasks:
            print(task.result())

if __name__ == '__main__':
    asyncio.run(main())
