# [Day26] 九翼 - Exception Groups與except*：相關應用
今天我們分享三個`Exception Groups`與`except*`的相關應用。
* 應用1：asyncio
* 應用2：retry
* 應用3：context manager

## 應用1：asyncio
`asyncio`是開發`Exception Groups`與`except*`的主要推手之一。Python3.11前處理`asyncio`最常使用的方法是`asyncio.gather`與`asyncio.wait`，而於Python3.11新添加了`asyncio.TaskGroup`。以下我們將分別使用三種方法來同時處理`# 00`內的四個`coroutine function`。
```python=
# 00
async def coro1():
    raise ValueError('1')


async def coro2():
    raise TypeError('2')


async def coro3():
    raise TypeError('3')


async def coro4():
    return 'coro4 is good'
```
如果對`asyncio`有想深入了解的朋友，我們相當推薦`Łukasz Langa`（`註1`）代表`EdgeDB`錄製的[asyncio介紹系列](https://www.youtube.com/watch?v=Xbl7XjFYsN4&list=PLhNSoGM2ik6SIkVGXWBwerucXjgP1rHmB)。

### Coroutine function vs Coroutine object
在開始分享之前，在`asyncio`的世界裡，我們需要很清楚分別何謂`coroutine`。

下面這段程式，是Python docs的例子。
```python=
import asyncio

async def nested():
    return 42

async def main():
    # Nothing happens if we just call "nested()".
    # A coroutine object is created but not awaited,
    # so it *won't run at all*.
    nested()

    # Let's do it differently now and await it:
    print(await nested())  # will print "42".

asyncio.run(main())
```
此外，其也很明白地[定義](https://docs.python.org/3/library/asyncio-task.html#awaitables)了`coroutine function`與`coroutine object`。
> a coroutine function: an async def function.
> a coroutine object: an object returned by calling a coroutine function.

簡單說，使用`async def`來定義的`function`稱為`coroutine function`；而呼叫`coroutine function`會返回一個`coroutine object`。雖然為了方便溝通，我們常常使用`coroutine`來同時代稱這兩種概念，但是作為優秀的Python開發者，我們一定要能清楚分辨兩者的不同。

### asyncio.gather
[asyncio.gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)的`signature`如下：
```python=
awaitable asyncio.gather(*aws, return_exceptions=False)
```
其可接收多個[awaitable](https://docs.python.org/3/library/asyncio-task.html#awaitables)，並有一個`return_exceptions`的flag。當`return_exceptions`為`True`時，會將例外與結果包在一個`list`中返回。如果為`False`的話，遇到第一個例外就會報錯，但是其它的`aws`並不會取消，而是會繼續執行。

#### `return_exceptions`為`True`時
```python=
# 01a
...

async def main():
    tasks = []
    coros = [coro1(), coro2(), coro3(), coro4()]
    for coro in coros:
        task = asyncio.create_task(coro)
        tasks.append(task)
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # results=[ValueError('1'), TypeError('2'), TypeError('3'), None]

    for result in results:
        match result:
            case ValueError() as msg:
                print(f'ValueError handling: {msg}')
            case TypeError() as msg:
                print(f'TypeError handling: {msg}')
            case _ as others:
                print(f'Rest: {others}')


if __name__ == '__main__':
    asyncio.run(main())
```
```
ValueError handling: 1
TypeError handling: 2
TypeError handling: 3
Rest: coro4 is good
```
從`results`中我們可以得到所以的結果及例外，但需要利用多個`if`或是新的`structural pattern matching`來分出各個情況。

#### `return_exceptions`為`False`時
```python=
# 01b
...

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
```
```
Traceback (most recent call last):
    ....
    raise ValueError('1')
ValueError: 1
```
`# 01b`中，當遇到第一個例外`ValueError('1')`即會返回，但是其它`aws`的工作並不會取消。

#### 注意事項
在建立`tasks`，很多人喜歡使用`list comprehensions`來做。沒錯，大部份情況下`list comprehensions`是個好點子，但在這邊或許不是...。有興趣了解為什麼的朋友可以參考`Will McGugan`(`註2`)寫的[解釋](https://textual.textualize.io/blog/2023/02/11/the-heisenbug-lurking-in-your-async-code/)。


### asyncio.wait
[asyncio.wait](https://docs.python.org/3/library/asyncio-task.html#asyncio.wait)的`signature`如下：
```python=
coroutine asyncio.wait(aws, *, timeout=None, return_when=ALL_COMPLETED)
```
其接受一個`aws`的`iterable`，`Timeout`及`return_when`的flag。
`return_when`共有三個選擇，預設為最常用的`ALL_COMPLETED`，其餘兩個為`FIRST_COMPLETED`與`FIRST_EXCEPTION`。其會返回兩個`set`，第一個`set`包含已經完成的`task`，第二個`set`則是未完成的`task`。一般使用的pattern會像這樣：
```python=
done, pending = await asyncio.wait(aws)
for p in pending:
    p.cancel()
    
for d in done:
    ...
```
一般`asyncio.wait`之後，我們會針對`pending`打一個迴圈，來取消未完成的工作。然後再對`done`打一個迴圈，取出其結果。


#### `return_when`為`ALL_COMPLETED`
我們使用預設的`return_when=ALL_COMPLETED`來解決問題。
* 處理`pending`時，`Or Chen`建議對每一個`pending` `task`都再`await asyncio.wait`一小段時間，確保它們都能順利被取消。
* 處理`done`時，由於裡面同時有`result`及`Exception`，所以必須在`try-except`中分開處理。
```python=
# 02a
...
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
```
```
handling 3
handling 1
coro4 is good
handling 2
```
由於這樣的pattern非常常用，`Or Chen`建議我們可以將大部份邏輯抽取到`wait` `coroutine function`並搭配`ExceptionGroup`使用。
```python=
# 02b
...

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
```
```
handling 2
handling 3
handling 1
```
`wait`內，可以分為三段：
* 第一段針對`aws`建立`task`。 
* 第二段執行`asyncio.wait`，並取消所有`pending` `task`，並多`await asyncio.wait`一次。
* 第三段為收集例外。如果有收例外的話，則生成一個`EG`返回；如果沒有的話就返回`done`。

於`main`中，我們就可以使用`try-except*`的語法來處理例外。

`# 02a`與`# 02b`其實並不完全相等。
* `# 02a`的寫法可以同時得到`result`「以及」處理例外。
* `# 02b`的寫法只能得到`result`「或是」處理例外。

實際上要用哪個方法，得視應用情況而定。

### asyncio.TaskGroup
`asyncio.TaskGroup`是一個`class`，我們實際要用的是它的`create_task` `function`，其`signature`如下：
```python=
create_task(coro, *, name=None, context=None)
```
`create_task`接受單個`coroutine`，並可接受`name`及`context`兩個參數。

其使用pattern會像：
```python=
async def main():
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(some_coro(...))
        task2 = tg.create_task(another_coro(...))
    print("Both tasks have completed now.")
```
* `async with`會自動`await`，直到`tg.create_task`所生成的`task`完成為止。
* 於等待期間，新的`task`還是可以加入(例如可以將`tg`可以傳到另一個`coroutine`內，再次使用`tg.create_task`)。
* 一旦所有`task`完成，離開`async with`的範圍後，就無法添加新`task`。
* 於執行`task`時，當遇到第一個非`asyncio.CancelledError`的例外時，所有剩下的`task`都會被取消，也不能加入新的`task`。此時，若程式還在`async with`的範圍內，則直接在`async with`內的`task`也會被取消。至於最後的`asyncio.CancelledError`只會形成`await`的情況，不會傳遞出`async with`。
* 當所有`task`完成後，若有例外發生的話，會集合成`ExceptionGroup`或`BaseExceptionGroup`(例外為`KeyboardInterrupt`及`SystemExit`時)。
* 程式若於離開`async with`出錯時(`__aexit__`被一個`exception set`呼叫時)，將會被視為任何一個`task`發生例外一樣，取消所有`task`，最後將無法取消的`task`集合成`EG`再`reraise`。傳入`__aexit__`的例外除非是`asyncio.CancelledError`，否則也會加入`EG`中(`KeyboardInterrupt`及`SystemExit`一樣是例外)。

#### 以`tg.create_task`代替`asyncio.create_task`
`# 03a`寫法相比於前面兩種精簡了不少，`task`不需顯性的`await`，當任一`task`遇到錯誤時也會自動取消。

```python=
# 03a
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
```
```
handling 1
handling 2
handling 3
```
由於`tg.create_task`要嘛是全部成功返回結果，要嘛是`raise EG`，所以我們使用`try-except*-else`的語法，於`except* Exception as eg`處理例外，於`else`中從`tasks`拿結果。

如果`task`不在乎回傳值的話，語法可以更簡潔。我們可以像`# 2b`一樣，將真正的操作獨立出去，只要處理`except* Exception as eg`就好，如`# 03b`。
```python=
# 03b
...

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
```
```
handling 1
handling 2
handling 3
```
另外，由於我們的四個`coroutine` `function`同時執行，當遇到第一個例外時，其它`task`其實也都執行完了，所以看不出來`asyncio.TaskGroup`可以幫忙取消`task`。

`# 03`中，我們將`coro1`、`coro2`及`coro3`加上時間不等的`asyncio.sleep`，這樣就可以看出，於`coro1`被發現有例外時，`coro2`及`coro3`都被取消了，而`coro4`已經執行完成。所以最後回傳的`EG`只有`coro1`中的` ValueError('1')`。
```python=
# 03c
import asyncio


async def coro1():
    await asyncio.sleep(1)
    raise ValueError('1')


async def coro2():
    await asyncio.sleep(2)
    raise TypeError('2')


async def coro3():
    await asyncio.sleep(3)
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
```
```
handling 1
```
### asyncio.TaskGroup實例
於結束`應用1`前，我們來舉一個使用`asyncio.TaskGroup`的實例。

我們的目標是以`asyncio.TaskGroup`建立三個`task`，同時對三個網址發出`request`，取回各自`response`後，以`json`格式儲存成三個`json`檔。當其中任一`task`報錯，`asyncio.TaskGroup`將會自動取消其它`task`。

我們將使用[JSONPlaceholder](https://jsonplaceholder.typicode.com/)的免費API，感謝他們。
#### Happy path
我們先假設在不需要處理例外的情況下，如何解決這個問題。
我們將此問題拆成四個`function`、`main`	、`download_many`	、`download`及`dump_json`

#### `main`
* 為`asyncio`的入口。
* 生成一個`task_info`，格式為`list`內含三個`tuple`。每個`tuple`的第一個元素為`task`的名字，第二個元素則為想下載的網址，
* 使用`httpx`library來發出`request`。
* 使用`built-in`的`contextvars.ContextVar`功能來取得及設定`httpx.AsyncClient`，如此可以免去顯性傳遞`client`。
* `await`實際工作的`download_many`。
* 由於不需要處理例外，所以我們可以直接印出每個`task`。
```python=
# 03d
import asyncio
import contextvars
import json
from pathlib import Path

import httpx

async_client_contextvar = contextvars.ContextVar('async_client')
...

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
```
```
task=<Task finished name='Get user_1_todos' coro=<download() done, defined at xxx.py:17> result=None>
task=<Task finished name='Get user_1_posts' coro=<download() done, defined at xxx.py.py:17> result=None>
task=<Task finished name='Get user_1_comments' coro=<download() done, defined at xxx.py:17> result=None>
```


##### download_many
`download_many`則是一個非常制式的`tg.create_task`模式，功用為包住`download`，建立`task`。
```python=
# 03d
...

async def download_many(taks_info):
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for task_name, url in taks_info:
            task = tg.create_task(download(url), name=task_name)
            tasks.append(task)
        return tasks
```
##### download
於`download`中我們針對給定網址發送`GET request`，並將`response`轉為`json`格式後，呼叫`dump_json`存為`json`檔案。
```python=
# 03d
...

async def download(url):
    file = Path('_'.join(url.split('/')[-3:])).with_suffix('.json')
    async_client = async_client_contextvar.get()
    resp = await async_client.get(url)
    content = resp.json()
    dump_json(file, content)
```
##### dump_json
呼叫`json.dump`寫入`json`檔案。
```python=
# 03d
...

def dump_json(file, content):
    with open(file, mode='w', encoding='utf-8') as f:
        json.dump(content, f, indent=4)
```

#### 例外處理
由於`Happy path`的情況實在太樂觀了，正所謂不出意外的話，就要出意外了。

我們在`download`過程中，不可避免的會遭遇到各種意外，例如`NetworkError`或`TimeoutException`。

我們在`download`內加上一些程式碼，使得每次執行`download`時，可能會：
* 正常執行。
* `raise httpx.NetworkError`。
* `raise httpx.TimeoutException`。
* 發生預期外的例外。

`await asyncio.sleep(0.1)`是為了防止各`task`執行太快，當其中一個有報錯時，已經執行完畢，看不出`asyncio.TaskGroup`的取消效果。

```python=
# 03e
import random

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
```
於`main`中，我們可以使用`except*`語法來補捉所有發生的例外。
```python=
# 03e
...

async def main():
    ...
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
```
下面列出一些可能的情況，供參考。
```
(NetworkError("Can not connect to url='https://jsonplaceholder.typicode.com/users/1/todos'"), NetworkError("Can not connect to url='https://jsonplaceholder.typicode.com/posts/1/comments'"))
(TimeoutException("Wait too long for check url='https://jsonplaceholder.typicode.com/users/1/posts'"),)
```
```
(NetworkError("Can not connect to url='https://jsonplaceholder.typicode.com/users/1/todos'"),)
(TimeoutException("Wait too long for check url='https://jsonplaceholder.typicode.com/posts/1/comments'"),)
```
```
(NetworkError("Can not connect to url='https://jsonplaceholder.typicode.com/posts/1/comments'"),)
```
```
task=<Task finished name='Get user_1_todos' coro=<download() done, defined at xxx.py> result=None>
task=<Task finished name='Get user_1_posts' coro=<download() done, defined at xxx.py> result=None>
task=<Task finished name='Get user_1_comments' coro=<download() done, defined at xxx.py> result=None>
```

## 應用2：retry
這個小節我們試著使用`decorator`並搭配`EG`。

我們的目標是建立一個`retry`的`decorator function`:
* 其可利用`@retry(max_retries=n)`的語法，來對被裝飾的`function`，進行`n`次的retry。
* 或是利用`@retry`的語法，來對被裝飾的`function`，執行預設次數（預設1次）的retry。
* 若retry結束，被裝飾的`function`仍然無法成功完成的話，會收集所有retry過程中的例外，生成一個`EG`返回。

`# 04`中的`my_func`為被`retry`所裝飾的`function`，其可能會`raise TypeError('1')`、`raise ValueError('2')`或成功返回`ok`。
```python=
# 04
...

@retry
def my_func():
    lot = random.choice([TypeError('1'), ValueError('2'),  'ok'])
    match lot:
        case TypeError():
            raise lot
        case ValueError():
            raise lot
        case _:
            return lot
```
接著實作`retry`:
* 於一開始做一個`max_retries`的檢查，若無法通過的話，`raise EG`。
* 接下來的`dec`是真正接收`my_func`的`decorator` `function`，其會返回內部真正執行計算的`wrapper`。
* 於`wrapper`內最多需執行`max_retries+1`次(`1`是指`my_func`本身要先執行一次，如果有不成功的情況，才會進行`max_retries`次的retry)。當成功得到結果後，立即返回，若有例外的話，就累積到`exceptions`中。在經過`max_retries+1`次重新呼叫`my_func`仍然沒有返回的話，代表有例外，於最後生成一個`EG`來包住`exceptions`並返回。
* 至於最後`return dec`或是`return dec(func)`這段，是方便我們可以同時使用`@retry`及`@retry()`兩種語法(可參考[[Day05]](https://ithelp.ithome.com.tw/articles/10317757)的內容)。
```python=
# 04
import random
from functools import wraps

def retry(func=None, /, max_retries=1):
    if not isinstance(max_retries, int) or max_retries < 0:
        raise ExceptionGroup('invalid max_retries',
                             (ValueError('max_retries must be an integer and >=0'),))

    def dec(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            exceptions = []
            runs = max_retries+1  # add the first invocation
            for i, _ in enumerate(range(runs), 1):
                print(f'{func.__name__} is running ({i}/{runs})')
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    exceptions.append(e)
            raise ExceptionGroup(
                f'Retry {max_retries} times but still failed', exceptions)
        return wrapper

    if func is None:
        return dec
    return dec(func)
...
```
最後執行程式，可能會有多種結果。而透過`except*`這個新語法，我們可以補抓到所有發生過的例外。
```python=
# 04
...

if __name__ == '__main__':
    try:
        print(f'{my_func()=}')  # 'ok'
    except* Exception as eg:
        print(eg.exceptions) 
        # 4 possibilities
        # (TypeError('1'), TypeError('1'))
        # (TypeError('1'), ValueError('2'))
        # (ValueError('2'), (TypeError('1'))
        # (ValueError('2'), ValueError('2'))
```
一些可能的結果供參考。
```
my_func is running (1/2)
my_func()='ok'
```
```
my_func is running (1/2)
my_func is running (2/2)
my_func()='ok'
```
```
my_func is running (1/2)
my_func is running (2/2)
(TypeError('1'), ValueError('2'))
```
```
my_func is running (1/2)
my_func is running (2/2)
(ValueError('2'), TypeError('1'))
```
## 應用3：context manager
這個小節我們準備建立一個實作有`context mnager protocol`的`class`，並觀察其於`__exit__`報錯時，於外層補抓例外的行為。

### `try-except`
我們先觀察傳統`try-except`的行為。
```python=
# 05a
from contextlib import AbstractContextManager


class DBCloseError(Exception):
    ...


class HTTPError(Exception):
    ...


class DBClient:
    def close(self):
        raise DBCloseError('Error occurred while closing db...')


class Connection(AbstractContextManager):
    def __init__(self):
        self._client = DBClient()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self._client.close()

    def do_something(self):
        return 'done'

    def send_report(self):
        raise HTTPError('Report is not sent.')


if __name__ == '__main__':
    try:
        with Connection() as conn:
            conn.do_something()
            conn.send_report()
    except HTTPError:
        print('handling HTTPError...')
    except DBCloseError:
        print('handling DBCloseError...')
```
```
handling DBCloseError...
```
* `conn.do_something()` 正常執行，沒有例外。
* `conn.send_report()`會`raise` `HTTPError`。
* 於離開`with Connection() as conn`時，`__exit__`中的`self._client.close()`會`raise DBCloseError`。
* 於最外層我們試著補抓`HTTPError`與`DBCloseError`，結果只會抓到`DBCloseError`。

我們真正想做的操作是`conn.do_something()`（無例外）及`conn.send_report()`（有例外），但因為離開`context manager`時也有例外，導致我們於外層只能補抓到`context manager`的例外，而無法補捉到真正操作發生的例外。

### `try-except*`
`except*`語法可以改變這種行為。

`# 05b`中。我們改在`__exit__`中先使用`try-except`補抓例外。如果有例外的話，我們將此例外與我們顯性`raise`的`e`，一起用一個`EG`包起來後回傳。
```python=
# 05b
...
class Connection(AbstractContextManager):
    ...
    def __exit__(self, exc_type, exc_value, exc_tb):
        try:
            self._client.close()
        except Exception as e:
            raise ExceptionGroup(
                'Got Exception while closing connection', [e, exc_value])
 
            
if __name__ == '__main__':
    try:
        with Connection() as conn:
            conn.do_something()
            conn.send_report()
    except* HTTPError:
        print('handling HTTPError...')
    except* DBCloseError:
        print('handling DBCloseError...')
```
這麼一來，我們在外層就可以同時補抓到兩種例外。
```
handling HTTPError...
handling DBCloseError...
```

## 參考資料
* [import asyncio: Learn Python's AsyncIO by EdgeDB](https://www.youtube.com/playlist?list=PLhNSoGM2ik6SIkVGXWBwerucXjgP1rHmB)
* [Lukasz Langa Keynote PyCon Colombia 2023](https://www.youtube.com/watch?v=B7U049ll4Rs)
* [How Exception Groups Will Improve Error Handling in AsyncIO - Łukasz Langa | Power IT Conference](https://www.youtube.com/watch?v=Lfe2zsGS0Js)
* [Asyncio Evolved: Enhanced Exception Handling with TaskGroup in Python 3.11 — Junya Fukuda](https://www.youtube.com/watch?v=FvWXyAXyb4Q)
* [SuperFastPython - How to use asyncio.TaskGroup](https://superfastpython.com/asyncio-taskgroup/)
* [Real Python - How to Catch Multiple Exceptions in Python](https://realpython.com/python-catch-multiple-exceptions/)
* [Real Python - Python 3.11 Preview: Task and Exception Groups](https://realpython.com/python311-exception-groups/#exception-groups-and-except-in-python-311)
## 備註
註1：[Łukasz Langa](https://lukasz.langa.pl/a072a74b-19d7-41ff-a294-e6b1319fdb6e/)是Python基金會雇請的第一位`CPython Developer in Residence`，並進入第三年任期。此外，他也常在各地的PyCon演講，錄影大多可以在YouTube上找到。我們覺得他的講解十分清楚，在他身上學了很多，非常感謝他的分享。

註2：`Will McGugan`是[Rich](https://github.com/Textualize/rich)和[Textual](https://github.com/Textualize/textual)兩個超酷library的創始人。如果您沒聽過他，又剛好有`terminal`方面的Python應用，絕對不要錯過這兩個library。


## Code
[本日程式碼傳送門](https://github.com/jrycw/py10wings/tree/master/src/09_exceptiongroups/day26_exceptiongroups_examples)。