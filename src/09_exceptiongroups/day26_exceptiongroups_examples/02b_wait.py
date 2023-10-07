# 02b
import asyncio
from typing import Awaitable, Iterable


async def coro1():
    raise ValueError('1')


async def coro2():
    raise TypeError('2')


async def coro3():
    raise TypeError('3')


async def coro4():
    return 'coro4 is good'


async def wait(aws: Iterable[Awaitable]) -> set[asyncio.Future]:
    # create tasks for aws
    tasks = []
    for aw in aws:
        if isinstance(aw, asyncio.Future):
            task = aw
        elif asyncio.iscoroutine(aw):
            task = asyncio.create_task(aw)
        else:
            raise TypeError('aws must all be awaitables')
        tasks.append(task)

    # wait
    done, pending = await asyncio.wait(tasks)
    for task in pending:
        task.cancel()
        await asyncio.wait(task, timeout=1)  # gracefully wait again

    # raise ExceptionGroup or return done
    exceptions = [exc for t in done if (exc := t.exception())]
    if exceptions:
        raise ExceptionGroup('Erros in aws', exceptions)
    return done


async def main():
    coros = [coro1(), coro2(), coro3(), coro4()]
    try:
        done = await wait(coros)
        for task in done:
            print(f'{task.result()}')
    except* Exception as eg:
        for exc in eg.exceptions:
            print(f'handling {exc}')

if __name__ == '__main__':
    asyncio.run(main())
