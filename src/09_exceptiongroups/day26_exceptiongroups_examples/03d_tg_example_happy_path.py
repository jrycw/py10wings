# 03d
import asyncio
import contextvars
import json
from pathlib import Path

import httpx

async_client_contextvar = contextvars.ContextVar('async_client')


def dump_json(file, content):
    with open(file, mode='w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)


async def download(url):
    file = Path('_'.join(url.split('/')[-3:])).with_suffix('.json')
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
        tasks = await download_many(taks_info)
        for task in tasks:
            print(f'{task=}')


if __name__ == '__main__':
    asyncio.run(main())
