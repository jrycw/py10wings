# [Day27] 末翼 - Term Projects：Project ECC - 建立EdgeDB Cloud Connection(1)

## 末翼大綱
末翼我們將實作兩個小project，來活用前面九翼的內容。

### Project ECC
[Day27]與[Day28]為project ECC，目標為實作一個可連接`EdgeDB Cloud`的`EdgeDB cloud connection`，並完成一個streamlit app作為前端。

* [[Day27]](https://ithelp.ithome.com.tw/articles/10317779)`EdgeDBCloudConn` `class`實作及實際測試。
* [[Day28]](https://ithelp.ithome.com.tw/articles/10317780)建立一個streamlit app，並使用`EdgeDBCloudConn`連接`EdgeDB Cloud`。

### Project postman
* [[Day29]](https://ithelp.ithome.com.tw/articles/10317781)為`Project postman`，目標為研究傳遞decorator factory參數的各種可能方法。

## ECC源起
於七月底到八月初參加了[strealit connections hackathon](https://discuss.streamlit.io/t/connections-hackathon/47574)比賽(因為參加比賽就有送一件薄帽T...)，使用`EdgeDB`的`Blocking API`實作。後來於八月底排到了`EdgeDB Cloud`的使用權限，加上又新學了`asyncio.TaskGroup`與`Exception Groups`，於是便想趁著鐵人賽，使用`EdgeDB`的`AsyncIO API`來重新實作看看。

## ECC目標
* 建立一個`EdgeDBCloudConn`的`class`，並實作`__aenter__`與`__aeit__`，使該`class`可以作為`async context manager`使用。
* 於進入`__aenter__`與`__aexit__`時，`logging`進入訊息。
* 於離開`__aexit__`時，`logging`實際database呼叫次數及實際在`context managet`中所經歷的時間。
* 可以使用async語法進行簡單`query`，並於每次`query`進行`logging`。
* `Read`的`query`需有快取機制。
* 不需著墨於`transactions`功能。

## EdgeDB
[EdgeDB](https://www.edgedb.com/)建基於`Postgres`之上，有著自己的`EdgeQL`語法與type system。其`EdgeQL query`會於底層compile為相對應的`Postgres query`，由於其不是一個`ORM`，所以理論上所有想對`Postgres`做的操作，應該都能使用更簡潔的`EdgeQL`語法達成。

Co-Founder兼CEO的[Yury Selivanov](https://github.com/1st1)是Python asyncio背後的主要推手，也是asyncio威力加強版[uvloop](https://github.com/MagicStack/uvloop)的主要開發者。因此不難想像`EdgeDB`從一開始就以async思維開發，因此其效率極高。下圖為官方的benchmark。

![benchmark](https://www.edgedb.com/benchmarks.svg)

`EdgeDB`各語言的[library](https://www.edgedb.com/docs/clients/index)都在活躍開發中，目前已經支援的有：
* Python
* TypeScript/JavaScript
* Go
* Rust
* .NET
* Java
* Elixir

其雲端服務[EdgeDB Cloud](https://www.edgedb.com/docs/guides/cloud)也已進入了Beta版，目前沒有對外開放，但可以加入watchlist或是到discord申請快速通關。


## EdgeDB-Python
[EdgeDB-Python](https://github.com/edgedb/edgedb-python)為官方提供的library。由於我們的是目標是建立async的connection，所以直接查找說明文件中[AsyncIO API](https://www.edgedb.com/docs/clients/python/api/asyncio_client#edgedb-python-asyncio-api-reference)。

經過一番查找之後，發現`edgedb.create_async_client`可以幫忙生成`AsyncIOClient`的`instance`，而`AsyncIOClient`提供六種不同情況的`query function`：
* AsyncIOClient.query()
* AsyncIOClient.query_single()
* AsyncIOClient.query_required_single()
* AsyncIOClient.query_json()
* AsyncIOClient.query_single_json()
* AsyncIOClient.query_required_single_json()

這幾個功能將是我們建立`EdgeDBCloudConn`的好幫手。

## ECC架構
`ECC`架構如下。
```
ECC
├── ecc
│   ├── __init__.py
│   ├── connection.py
│   ├── data_structures.py
│   ├── queries.py
│   └── utils.py
│── edgedbcloud.toml
└── tests
    ├── __init__.py
    ├── test_healthy.py
    ├── test_imqry.py
    ├── tests_mqry.py
    ├── tests_qry_by_args.py
    └── utils.py
```
* `ecc/connection.py`：`EdgeDBCloudConn` `class`。
* `ecc/data_structures.py`：`Enum`及`Namedtuple`等資料結構。
* `ecc/queries.py`：提供寫好的`EdgeQL`。
* `ecc/utils.py`：小工具。

### data_structures.py
內有兩個`Enum`及一個`NamedTuple`。

#### `RespJson(Enum)`
內有`NO`及`YES`兩個member，並使用`enum.auto`為其自動賦值。其功用是用來區別，`query`是否需要返回`json`格式，會於`QueryRecord` 中使用。
```python=
from enum import Enum, auto


class RespJson(Enum):
    NO = auto()
    YES = auto()
```
#### `RespConstraint(Enum)`
內有`FREE`、`NO_MORE_THAN_ONE`及`EXACTLY_ONE`三個member，並使用`enum.auto`為其自動賦值。其功用是用來區別，是否需要檢驗`query`返回結果長度，會於`QueryRecord` 中使用。

```python=
...

class RespConstraint(Enum):
    FREE = auto()
    NO_MORE_THAN_ONE = auto()
    EXACTLY_ONE = auto()
```
#### `QueryRecord(NamedTuple)`
* `qry`(`str`)：`EdgeQL`語法的`query` `str`。
* `extra_args`(`tuple`)：當需要`Filter`時使用。
* `jsonify`(`RespJson`)：返回結果是否為`json`格式。
* `required_single`(`RespConstraint`)：是否檢驗返回結果長度。
* `extra_kwargs`(`dict`)：當需要`Filter`時使用。
* `task_name`(`str`)：`asyncio task`的`task name`。

```python=
...
from typing import NamedTuple


class QueryRecord(NamedTuple):
    qry: str
    extra_args: tuple[Any, ...]
    jsonify: RespJson
    required_single: RespConstraint
    extra_kwargs: dict[str, Any]
    task_name: str
```

### utils.py
#### `get_logger`
為一個輔助`function`來幫助我們取得`logger instance`。由於[logging.getLogger](https://docs.python.org/3/library/logging.html#logging.getLogger)是一個`module-level function`，只要名字不變的話，每次呼叫都可以取回同一個`instance`，所以不用顯性以參數在各個`obj`中傳遞。
```python=
def get_logger(logger_name: str = 'edgedb-cloud') -> logging.Logger:
    return logging.getLogger(logger_name)
```

#### `load_toml`
建立`edgedbcloud.toml`作為設定檔，並於其中定義一個`edgedb-cloud` `table`，輸入所需的參數。
* `host`需要由[EdgeDB cli](https://www.edgedb.com/docs/cli/edgedb_cloud/edgedb_cloud_login)登入`EdgeDB cloud`後，才能於`command line`或`REPL`中取得。
* `EdgeDB`預設使用`port` `5656`。
* `secret_key`可以由[指令](https://www.edgedb.com/docs/cli/edgedb_cloud/edgedb_cloud_secretkey/edgedb_cloud_secretkey_create#ref-cli-edgedb-cloud-secretkey-create)取得，也可以由`EdgeDB Cloud`的UI取得。
* `database`為`_example`。其為`EdgeDB`提供練習用的`database`，可於`EdgeDB Cloud`中一鍵生成。
* `ttl`為`immutable query`的快取時間。

```toml=
[edgedb-cloud]
host = 'xxx.aws.edgedb.cloud'
port = 5656
secret_key = 'secret_key'
database = '_example'
ttl = 5
```

`load_toml`接受`toml_name`與`table_name`兩個參數，並回傳一個`dict`，其內是`toml_name`中`table_name`的所有參數。Python於3.11加入了[tomllib](https://docs.python.org/3/library/tomllib.html)模組，幫助我們讀取`toml`格式的檔案。請注意文件中特別指出`tomllib.load`需接受`readable`的`binary object`，所以於`open`的`mode`需指定為`rb`。
```python=
def load_toml(toml_name: str = 'edgedbcloud.toml',
              table_name: str = 'edgedb-cloud') -> dict[str, Any]:
    with open(toml_name, 'rb') as f:
        data: dict[str, dict[str, Any]] = tomllib.load(f)
    return data[table_name]
```

#### `match_func_name`
幫助我們選擇`AsyncIOClient` `query function`的小工具。

`AsyncIOClient`的六種`query function`可以分成兩個大類：
* 一類是這個`query`是否需要返回`json`格式，可依`function`名最後是否有`_json`來判斷。
* 一類是返回結果的長度，是否符合預期，總共又分成三類：
    * 不設限制，`function`名為`query`開頭。
    * 回傳長度不能超過一，`function`名為`query_single`開頭。
    * 回傳長度必須恰恰是一，`function`名為`query_required_single`開頭。

於是我們開始思考，如何用`jsonify`與`required_single`兩個參數來組合出這六個`function`呢？此外，又要用什麼來區別各種可能的值呢？神奇的`12345`？還是`singleton`的`True`、`False`、`None`等？

Python的`Enum`可能是一個不錯的解決方法，於是我們在`data_structures.py`建立了`RespJson`與`RespConstraint`兩個`Enum`。值得一提的是，因為我們只會比較`Enum` `member`的`entity`，而不會比較其值，所以其值是多少並不重要，這也是為什麼會使用`enum.auto`自動賦值的原因。

`match_func_name`依靠`structural pattern matching`的[match enum](https://peps.python.org/pep-0636/#matching-against-constants-and-enums)的功能，來取得相對應的`function`名。我們於`match_func_name`的最後，有設定一個`catch all`的`case _`，並於其中使用Python3.11新增的`assert_never`。

```python=
def match_func_name(jsonify: RespJson, required_single: RespConstraint) -> str:
    match (jsonify, required_single):
        case (RespJson.NO, RespConstraint.FREE):
            func_name = 'query'
        case (RespJson.NO, RespConstraint.NO_MORE_THAN_ONE):
            func_name = 'query_single'
        case (RespJson.NO, RespConstraint.EXACTLY_ONE):
            func_name = 'query_required_single'
        case (RespJson.YES, RespConstraint.FREE):
            func_name = 'query_json'
        case (RespJson.YES, RespConstraint.NO_MORE_THAN_ONE):
            func_name = 'query_single_json'
        case (RespJson.YES, RespConstraint.EXACTLY_ONE):
            func_name = 'query_required_single_json'
        case _ as unreachable:
            assert_never(unreachable)
    return func_name
```

### queries.py
#### `pack_imqry_records`
預先打包八種常用的`immutable` `query`為一`list`，作為測試之用。每個`query`型式都是一個`QueryRecord`的`instance`。
```python=
def pack_imqry_records() -> list[QueryRecord]:
    qries = ['SELECT Movie {title};',
             *['''SELECT assert_single(
                         (SELECT Movie {title, release_year} 
                          FILTER .title=<str>$title and 
                                 .release_year=<int64>$release_year));''']*3,
             'SELECT Account {username};',
             *['''SELECT assert_single(
                         (SELECT Account {username} 
                          FILTER .username=<str>$username))''']*3]
    args_collector = [()]*8
    jsons = [*[RespJson.NO]*4, *[RespJson.YES]*4]
    required_singles = [RespConstraint.FREE,
                        *[RespConstraint.NO_MORE_THAN_ONE]*2,
                        RespConstraint.EXACTLY_ONE]*2
    kwargs_collector = [{},
                        {'title': 'Ant-Man', 'release_year': 2015},
                        {'title': 'Ant-Man100', 'release_year': 2015},
                        {'title': 'Ant-Man', 'release_year': 2015},
                        {},
                        {'username': 'Alice'},
                        {'username': 'AliceCCC'},
                        {'username': 'Alice'}]
    task_names = [*[f'QueryMovie{n}' for n in range(4)],
                  *[f'QueryAccount{n}' for n in range(4)]]

    return [QueryRecord(*qr)
            for qr in zip(qries,
                          args_collector,
                          jsons,
                          required_singles,
                          kwargs_collector,
                          task_names)]
```

#### `pack_mqry_records`
與`pack_imqry_records`類似，只是包含的是兩種`mutable` `query`。

```python=
def pack_mqry_records() -> list[QueryRecord]:
    qries = ['''WITH p := (INSERT Person {name:=<str>$name}) 
           SELECT p {name};''',
             '''WITH p:= (DELETE Person FILTER .name=<str>$name) 
           SELECT p {name};''']
    args_collector = [()]*2
    jsons = [RespJson.NO]*2
    required_singles = [RespConstraint.FREE]*2
    kwargs_collector = [{'name': 'Adam Gramham'}]*2
    task_names = ['insert', 'delete']

    return [QueryRecord(*qr)
            for qr in zip(qries,
                          args_collector,
                          jsons, required_singles,
                          kwargs_collector,
                          task_names)]
```
#### `pack_imqry_records_by_args`
為測試是否能順利使用像`$0`或`$1`的語法進行`query`， 目前僅包含一個`immutable` `query`。

```python=
def pack_imqry_records_by_args() -> list[QueryRecord]:
    qries = ['''SELECT Movie {title, release_year} 
                FILTER .title=<str>$0 and .release_year=<int64>$1;''']
    args_collector = [('Ant-Man', 2015)]
    jsons = [RespJson.NO]
    required_singles = [RespConstraint.FREE]
    kwargs_collector: list[dict[str, Any]] = [{}]
    task_names = ['QueryMovieTitleByArgs']

    return [QueryRecord(*qr)
            for qr in zip(qries,
                          args_collector,
                          jsons,
                          required_singles,
                          kwargs_collector,
                          task_names)]
```



### connection.py
其內只有`EdgeDBCloudConn` `class`。

當`database`在一定時間內，通常不會變動的情況下，可以設定一個快取時間`ttl`。在`ttl`內如果使用同樣的`query`與參數來讀取資料時，可以直接回傳快取結果，而不真正呼叫`database`。

但是當`database`頻繁變動的話，對這類`query`進行快取就有很多眉角要注意。究竟使用者是真的想要快速發出多次同樣的`mutable` `query`，還是可能因為網路問題或`retry`等邏輯沒寫好，不小心發送多次，而我們應該只呼叫一次`database`就好？

因此我們決定`EdgeDBCloudConn`預設`ttl=0`，即沒有快取。當`ttl>0`時，會使用`alru_cache`來將`_imquery`包上快取設定，而`_mquery`則一律執行。



#### 繼承`AbstractAsyncContextManager`
[contextlib.AbstractAsyncContextManager](https://docs.python.org/3/library/contextlib.html#contextlib.AbstractAsyncContextManager)是Python提供的`abstract base class`。由於`EdgeDBCloudConn` `class`將會實作`__aenter__`與`__aexit__`，所以在此繼承`AbstractAsyncContextManager`是個絕佳的應用。
```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
```

#### `__init__`
共接收七個變數（`註2`）。
* `host`、`port`、`database`與`secret_key`將由`load_toml`讀取`edgedb.toml`所得，為實際建立連接所需要的參數。
* `ttl`為設定的快取時間，預設為`0`，即不快取。
* `logger`為指定的`logger instance`。當沒有指定的時候，會呼叫`get_logger`來取得一個預設的`logger`。
* `log_level`為想要記錄的層級，當沒有指定的時候，設定為`logging.INFO`。

因為`logger`及`log_level`，這兩個變數所要傳遞的值比較明確，所以我們使用了`or`的語法，而不顯性比較是否為`None`。

此外：
* `self._client`將會是`AsyncIOClient`建立的`client`之變數名，先預設為`None`。
* `self._start`為計算進入`__aenter__`與離開`__aexit__`所用時間之用。
* `self._dbcalls`為計算於`__aenter__`與`__aexit__`中實際呼叫`database`的次數之用。
* `self._total_dbcalls`為計算實際呼叫`database`的總次數之用。

最後一個`if`是用來設定`immutable query`的快取機制。這個手法相當微妙，這使得我們將會由`self.__dict__`中來存取`self._imquery`。現在的情況是：
* 由於`self._imquery`為一般`function`，只是`non-data descriptor`而不是`data descriptor`，所以當我們使用`self._imquery = alru_cache(ttl=ttl)(self._imquery)`的語法時，相當於在`self.__dict__`中，加入一個已經包過`alru_cache(ttl=ttl)`的`_imquery`。
* `EdgeDBCloudConn.__dict__`中，還是保有原來沒加上`alru_cache`的`_imquery`。

```python=
    def __init__(self,
                 *,
                 host: str,
                 port: int,
                 database: str,
                 secret_key: str,
                 ttl: float = 0,
                 logger: logging.Logger | None = None,
                 log_level: int | None = None) -> None:
        self._host = host
        self._port = port
        self._database = database
        self._secret_key = secret_key
        self._logger = logger or get_logger()
        self._log_level = log_level or logging.INFO
        self._logger.setLevel(self._log_level)

        self._client: EdgeDBAsyncClient | None = None
        self._start = 0.0
        self._dbcalls = 0
        self._total_dbcalls = 0

        if ttl > 0:
            self._imquery = alru_cache(ttl=ttl)(self._imquery)
```
#### `client`
為一`property`，用來包住底層的`self._client`。由於我們希望只建立一個`client`，所以每當`self.client`被呼叫時，我們會先檢查`self._client`是否為`None`，如果是的話，表示我們還沒有建立`client`，此時會先呼叫`edgedb.create_async_client`並搭配由`load_toml`所提供的各個參數來建立`async-client`。由於在建立`client`後，就不需要用到`self._secret_key`，與其讓它待在`instance`內，我們選擇刪除它。最後回傳`self._client`。

```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    @property
    def client(self) -> EdgeDBAsyncClient:
        if self._client is None:
            self._client = edgedb.create_async_client(host=self._host,
                                                      port=self._port,
                                                      database=self._database,
                                                      secret_key=self._secret_key)
            del self._secret_key
        return self._client
```
#### `_get_client_qry_func`
幫助我們實際由`self.client`，取到名字為`match_func_name`回傳值的`function`。

```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...

    def _get_client_qry_func(self,
                             jsonify: RespJson,
                             required_single: RespConstraint) -> Callable[..., Any]:
        return getattr(self.client, match_func_name(jsonify, required_single))
```

#### `get_cur_timestamp`
為回傳`timestamp`的`function`，可以幫助計算快取時間。`get_cur_timestamp`雖與`self`或`cls`的狀態無關，卻是`EdgeDBCloudConn` `class`的好幫手，所以我們設計其為static method。
```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    @staticmethod
    def get_cur_timestamp() -> float:
        return datetime.now().timestamp()
```

#### `_is_qry_immutable`
是用來判斷我們的`query`內是否含有，可能會`mutate` database的關鍵字。我們定義當`query`內含有`insert`、`update`或 `delete`時，就將此`query`判定為會`mutate` `database`。由於`_mutated_kws`不會隨著不同`instance`而改變，所以我們將其設為`class variable`。

```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    _mutated_kws = ('insert', 'update', 'delete')
    
    ...
    
    def _is_qry_immutable(self, qry: str) -> bool:
        return all(mutated_kw not in qry.casefold()
                   for mutated_kw in self._mutated_kws)
```

#### `query`、`_query`、`_imquery`與`_mquery`
這四個都是`async` `function`。`query`會依照`_is_qry_immutable`判斷該將`query`轉到`_imquery`或是`_mquery`。而`_imquery`與`_mquery`程式其實完全一樣，都是再將`query`轉到`_query`。這樣的用意是方便我們於`__init__`中於`ttl>0`時，可以動態加上`alru_cache`至`_imquery`。

```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    async def query(self,
                    qry: str,
                    *args: Any,
                    jsonify: RespJson = RespJson.NO,
                    required_single: RespConstraint = RespConstraint.FREE,
                    **kwargs: Any) -> QueryResult:
        if self._is_qry_immutable(qry):
            return await self._imquery(qry,
                                       *args,
                                       jsonify=jsonify,
                                       required_single=required_single,
                                       **kwargs)
        return await self._mquery(qry,
                                  *args,
                                  jsonify=jsonify,
                                  required_single=required_single,
                                  **kwargs)

    async def _imquery(self,
                       qry: str,
                       *args: Any,
                       jsonify: RespJson = RespJson.NO,
                       required_single: RespConstraint = RespConstraint.FREE,
                       **kwargs: Any) -> QueryResult:
        return await self._query(qry,
                                 *args,
                                 jsonify=jsonify,
                                 required_single=required_single,
                                 **kwargs)

    async def _mquery(self,
                      qry: str,
                      *args: Any,
                      jsonify: RespJson = RespJson.NO,
                      required_single: RespConstraint = RespConstraint.FREE,
                      **kwargs: Any) -> QueryResult:
        return await self._query(qry,
                                 *args,
                                 jsonify=jsonify,
                                 required_single=required_single,
                                 **kwargs)
```
`_query`中：
* 以`logging.info`記錄其實際被呼叫。
* 將`self._dbcalls`加上`1`。
* 使用`_get_client_qry_func`取回的`function`，搭配`qry`、`*args`及`**kwargs`進行呼叫，並回傳計算結果。
```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    async def _query(self,
                     qry: str,
                     *args: Any,
                     jsonify: RespJson = RespJson.NO,
                     required_single: RespConstraint = RespConstraint.FREE,
                     **kwargs: Any) -> QueryResult:
        self._logger.info(self._fmt_query_log_msg(
            qry, args, jsonify, required_single, kwargs))
        self._dbcalls += 1
        qry_func = self._get_client_qry_func(jsonify, required_single)
        return await qry_func(qry, *args, **kwargs)
```

#### `__aenter__`
* 於進入時，以`logging.info`記錄。
* 呼叫`self.get_cur_timestamp()`將其值賦予`self._start`。
```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    async def __aenter__(self) -> Self:
        self._logger.info(self._fmt_enter_aenter_log_msg())
        self._start = self.get_cur_timestamp()
        return self
```

#### `__aexit__`
* 開頭使用`await asyncio.sleep(1e-5)`的原因是，這樣可以方便UI可以即時更新。
* 進行兩次`logging.info`，一次記錄已經進入`__aexit__`，另一次記錄實際呼叫`database`次數。
* 如果有`exception`發生的話，以`logging.error`記錄。
* 將`self._dbcalls`加總至`self._total_dbcalls`後，呼叫`self._reset_db_calls`重設`self._dbcalls`為0。
* 離開`__aexit__`前，計算在`with`中的時間，並以`logging.info`記錄。
* 最後於離開`__aexit__`，呼叫`self._reset_start`重設`self._start`為`0.0`。
```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    async def __aexit__(self,
                        exc_type: type[BaseException] | None,
                        exc_value: BaseException | None,
                        exc_tb: TracebackType | None) -> None:
        await asyncio.sleep(1e-5)
        self._logger.info(self._fmt_enter_aexit_log_msg())
        self._logger.info(self._fmt_db_calls_log_msg())
        if exc_type:
            self._logger.error(self._fmt_aexit_exception_log_msg(exc_value))
        self._total_dbcalls += self._dbcalls
        self._reset_db_calls()
        elapsed = self.get_cur_timestamp() - self._start
        self._logger.info(self._fmt_exit_aexit_log_msg(elapsed))
        self._reset_start()
```

#### `aclose`
可以顯式呼叫底層`client`的`self.client.aclose`。請注意我們在`__aexit__`內，並沒有顯式的呼叫`await self.aclose()`，原因是現在很多database都具有pooling的機制，包括[EdgeDB](https://www.edgedb.com/blog/edgedb-release-candidate-2#concurrency)。
```python=
    async def aclose(self, timeout: float = 5) -> None:
        print('aclose called')
        await asyncio.wait_for(self.client.aclose(), timeout) 
```

#### `_healthy_check_url`與`is_healthy`
`_healthy_check_url`是`EdgeDB`內建能判斷`database`現在狀態的`url`（`註3`）。

`is_healthy`針對`self._healthy_check_url`發出`GET` request，並檢查返回`status_code`是否為`200`，來判斷`database`是否健康。如果遭遇到任何錯誤，設定回傳`False`。

```python=
class EdgeDBCloudConn(AbstractAsyncContextManager):
    ...
    
    @property
    def _healthy_check_url(self) -> str:
        return f'https://{self._host}:{self._port}/server/status/alive'

    @property
    def is_healthy(self) -> bool:
        """https://www.edgedb.com/docs/guides/deployment/health_checks#health-checks"""
        try:
            return httpx.get(self._healthy_check_url,
                             follow_redirects=True,
                             verify=False,
                             timeout=30).status_code == 200
        except httpx.HTTPError:
            return False
```

#### `_fmt_*`
開頭的多個`function`皆為返回`str`，供`logger`所用，在此不加贅述。

#### `_reset_*`
開頭的多個`function`為重設時間或資料庫呼叫次數所用。

### tests.py
總共有四個`TestClass`，都是實際對`database`進行`query`，沒有`mocking`（`註4`）。
* `TestHealthy`測試`_healthy_check_url`及`is_healthy`。
* `TestImqryCachedConn`測試在少量及大量`query`時都有進行快取。
* `TestImqryNonCachedConn`測試其沒有快取機制。
* `TestMqryConn`測試其沒有快取機制，且可正常`insert`及`delete`。


## 備註
註1：由於這個project的目標是建立與`EdgeDB cloud`連結的`connection`，而不是學習`EdgeQL`的語法。如果是對其語法有興趣的朋友：
* 可以參考[說明文件](https://www.edgedb.com/docs/edgeql/index)。
* 或是從[Easy EdgeDB](https://www.edgedb.com/easy-edgedb)開始學習，它就像一本20回的小說一樣，學習起來十分有趣。其作者為[Dave MacLeod](https://www.youtube.com/@mithradates)，在YouTube上有不少精彩的`Rust`影片解說，此外其也是[Learn Rust in a Month of Lunches](https://www.manning.com/books/learn-rust-in-a-month-of-lunches)的作者。


註2：如果您想要的是一個可以連接`local`或是`host`在其它雲端的`EdgeDB` `connection`，需要考慮較複雜的建立方式，包括支援[DSN](https://www.edgedb.com/docs/reference/dsn#dsn-specification)。

註3：如果這是連接`local`或是`ip`的`connection`，此`healthy_check_url`網址可能使用`http`而非`https`。

註4：當在Windows上測試時，會出現`ResourceWarning: Enable tracemalloc to get the object allocation traceback`，需要再研究資源關閉的問題。

## Code
[本日程式碼傳送門](https://github.com/jrycw/st-edgedb-cloud-conn)。