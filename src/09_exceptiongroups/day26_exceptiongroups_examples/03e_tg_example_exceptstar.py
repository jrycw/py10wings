# 03e
import asyncio
import contextvars
import json
import random
from pathlib import Path

import httpx

async_client_contextvar = contextvars.ContextVar('async_client')


def dump_json(file, content):
    with open(file, mode='w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)


def random_bool():
    return random.choice((True, False))


async def download(url):
    file = Path('_'.join(url.split('/')[-3:])).with_suffix('.json')

    # emulate exceptions happened
    filename = str(file)
    if '_todos' in filename and random_bool():
        raise httpx.NetworkError(f'Can not connect to {url=}')
    elif '_posts' in filename and random_bool():
        raise httpx.TimeoutException(f'Wait too long for check {url=}')
    elif '_comments' in filename and random_bool():
        if random_bool():
            raise httpx.NetworkError(f'Can not connect to {url=}')
        else:
            raise httpx.TimeoutException(f'Wait too long for check {url=}')
    await asyncio.sleep(0.1)

    async_client = async_client_contextvar.get()
    resp = await async_client.get(url)
    content = resp.json()
    dump_json(file, content)


async def download_many(taks_info):
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for task_name, url in taks_info:
            task = tg.create_task(download(url), name=task_name)
            tasks.append(task)
        return tasks


async def main():
    taks_info = [('Get user_1_todos',
                  'https://jsonplaceholder.typicode.com/users/1/todos'),
                 ('Get user_1_posts',
                  'https://jsonplaceholder.typicode.com/users/1/posts'),
                 ('Get user_1_comments',
                  'https://jsonplaceholder.typicode.com/posts/1/comments')]
    async with httpx.AsyncClient() as client:
        async_client_contextvar.set(client)
        try:
            tasks = await download_many(taks_info)
        except* httpx.NetworkError as ne_group:
            print(ne_group.exceptions)
        except* httpx.TimeoutException as te_group:
            print(te_group.exceptions)
        except* Exception as other_group:
            print(other_group.exceptions)
        else:
            for task in tasks:
                print(f'{task=}')

if __name__ == '__main__':
    asyncio.run(main())
