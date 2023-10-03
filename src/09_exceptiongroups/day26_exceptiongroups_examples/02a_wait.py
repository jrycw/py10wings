# 02a
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
    done, pending = await asyncio.wait(tasks)
    for pt in pending:
        pt.cancael()
        await asyncio.wait(pt, timeout=1)

    for task in done:
        try:
            if exc := task.exception():
                raise exc
            else:
                print(f'{task.result()}')
        except Exception as e:
            print(f'handling {e}')


if __name__ == '__main__':
    asyncio.run(main())
