# [Day28] 末翼 - Term Projects : Project ECC - 建立EdgeDB Cloud Connection(2)

## streamlit app目標
使用streamlit建立一個可以輸入`EdgeQL`、`query_args`及`query_kwargs`的`form`，並於`submit`之後，傳送`query`至`EdgeDB Cloud`執行（`註1`）。

下面是我們錄製一小段操作app的過程，可以點選圖片觀看。
[![ecc-demo-video](https://py10wings.jp-osa-1.linodeobjects.com/day28/ecc-streamlit-cloud.png)](https://py10wings.jp-osa-1.linodeobjects.com/day28/ecc-demo.mp4)

## streamlit app架構
```
ECC
├── ...
├── st_comps.py
├── st_data_structures.py
├── st_utils.py
└── streamlit_app.py
```

### st_comps.py
為擺放各種streamlit的widget及element的檔案。

### st_data_structures.py
只有一個`FormContent`的`NamedTuple`，於收集`form`內容時使用。

### st_utils.py
內有著許多小工具，我們挑選幾個比較重要的`function`來說明。

#### `get_loop_dict`與`get_conn_dict`
皆使用`@st.cache_resource`裝飾。這麼一來當任何`session`一進來，都可以取得同一個`loop_dict`與`conn_dict`，可以幫助我們使用現在的`timestamp`與存在其中的`timestamp`進行對比，進而執行想要的操作。
```python=
@st.cache_resource
def get_loop_dict() -> dict[str, Any]:
    return {}


@st.cache_resource
def get_conn_dict() -> dict[str, Any]:
    return {}
```
#### `_routine_clean`
會取得現在的`timestamp`，以此計算`get_loop_dict`與`get_conn_dict`中是否有超過`threshold`的`loop`或`conn`。相當於每次呼叫`streamlit_app.py`時，會定時清除閒置過久的資源。
```python=
def _routine_clean(excluded_tokens: list[str],
                   threshold: float = 300) -> None:
    cur_ts = get_cur_ts()

    ld = get_loop_dict()
    to_del_loop_tokens = {t
                          for t, (_, loop_ts) in ld.items()
                          if cur_ts - loop_ts > threshold}
    for _token in excluded_tokens:
        to_del_loop_tokens.discard(_token)
    for k in to_del_loop_tokens:
        try:
            del ld[k]
        except Exception as ex:
            st.toast(f'{ex=} happened in del loops', icon="🚨")

    cd = get_conn_dict()
    to_del_conn_tokens = {t
                          for t, (_, conn_ts) in cd.items()
                          if cur_ts - conn_ts > threshold}
    for _token in excluded_tokens:
        to_del_conn_tokens.discard(_token)
    for k in to_del_conn_tokens:
        try:
            del cd[k]
        except Exception as ex:
            st.toast(f'{ex=} happened in del conns', icon="🚨")
```
#### `_populate_qry_args`
將接收到的`str`以`;`分隔，接著檢查各個`arg_str`是否為支援的型態。如果是的話，嘗試使用`eval(arg_str)`取得轉換後的型態，再`append`到`qry_args`，最後返回`return tuple(qry_args)`。

```python=
def _populate_qry_args(qry_args_str: str) -> tuple[Any, ...]:
    qry_args: list[Any] = []
    for arg_str in qry_args_str.split(';'):
        if arg_str.strip() and \
                isinstance(arg_str, (str, datetime.date, datetime.datetime)):
            try:
                eval_arg = eval(arg_str)
            except SyntaxError as e:
                st.warning(
                    'Can not parse the positional query arguments!')
                raise e
            else:
                qry_args.append(eval_arg)
    return tuple(qry_args)
```

#### `_populate_qry_kwargs`
將接收到的`str`以`;`分隔，接著嘗試使用`exec(kwarg_str.strip(), globals(), qry_kwargs)`，將`kwarg_str` `populate`到`qry_kwargs`中，並於最後返回`qry_kwargs`。

```python=
def _populate_qry_kwargs(qry_kwargs_str: str) -> dict[str, Any]:
    qry_kwargs: dict[str, Any] = {}
    for kwarg_str in qry_kwargs_str.split(';'):
        try:
            exec(kwarg_str.strip(), globals(), qry_kwargs)
        except SyntaxError as e:
            st.warning(
                'Can not parse the named query arguments!')
            raise e
    return qry_kwargs
```

#### `_convert_form_to_record`
將`form`接收的內容轉換為`QueryRecord`格式。

我們曾經想在`_receive_required_single`中的`st.radio`使用`Enum`，但streamlit常會報錯，所以只好接收`str`型態再使用`convert_str_to_required_single`轉為`Enum`。

```python=
def _convert_form_to_record(form: FormContent) -> QueryRecord:
    qry = form.qry
    extra_args = _populate_qry_args(form.qry_args_str)
    jsonify = convert_bool_to_jsonify(form.jsonify)
    required_single = convert_str_to_required_single(form.required_single)
    extra_kwargs = _populate_qry_kwargs(form.qry_kwargs_str)
    task_name = uuid.uuid4().hex[:6]

    return QueryRecord(qry,
                       extra_args,
                       jsonify,
                       required_single,
                       extra_kwargs,
                       task_name)
```

#### `_create_task_from_form`
使用傳入的`tg`來新增`task`。

```python=
async def _create_task_from_form(tg: asyncio.TaskGroup,
                                 conn: EdgeDBCloudConn,
                                 form: FormContent,
                                 tasks: set[asyncio.Task[Any]]) -> None:
    record = _convert_form_to_record(form)
    async with conn:
        task = tg.create_task(conn.query(record.qry,
                                         *record.extra_args,
                                         jsonify=record.jsonify,
                                         required_single=record.required_single,
                                         **record.extra_kwargs),
                              name=record.task_name)
        tasks.add(task)
```


### streamlit_app.py
#### 建立`loop`
我們希望多個`session`能同時獨立操作，所以需要針對每個`session`建立`loop`及`conn`，無法簡單的呼叫`asyncio.run`就好。由於`loop`及`conn`都需要在每個`session`一開始就確定下來，所以如果將`_prepare_loop`或`_prepare_conn`移至其它檔案會出現問題。
```python=
...
import nest_asyncio

nest_asyncio.apply()

if 'token' not in st.session_state:
    token = generate_token()
    logging.info(f'Generating token: {token}')
    st.session_state['token'] = token


if __name__ == '__main__':
    cur_ts = get_cur_ts()
    token = st.session_state.token
    excluded_tokens = [token]

    loop = _prepare_loop(cur_ts, token)
    conn = _prepare_conn(cur_ts, token)

    _display_res(token, loop, conn, excluded_tokens)
    _routine_clean(excluded_tokens)

    asyncio.set_event_loop(loop)
    loop.run_until_complete(run(main, conn, token))
```
* 於每個`session`一開始時，呼叫`generate_token`產生獨特的`token`，並儲存於`st.session_state`中。
* 呼叫`_prepare_loop`準備`loop`。
* 呼叫`_prepare_conn`準備`conn`。
* 呼叫`_display_res`於最上方顯示`resource`，並生成`refresh`與`try free resource`兩個button。
* 呼叫`_routine_clean`定時清理`loop`與`conn`。
* 透過`asyncio.set_event_loop`設定`loop`。
* 透過`loop.run_until_complete`執行`run`，啟動event loop。


#### `_prepare_loop`
* 透過`get_loop_dict`取得`loop_dict`。
* 接著檢查`token`是否在`loop_dict`中。如果不在的話，呼叫`asyncio.new_event_loop`建立一個新`loop`;如果在的話，從中取出`loop`。
* 透過`loop_dict[token] = (loop, cur_ts)`更新`timestamp`。
* 最後返回`loop`。
```python=
def _prepare_loop(cur_ts: int, token: str) -> asyncio.AbstractEventLoop:
    loop_dict = get_loop_dict()
    if token not in loop_dict:
        loop = asyncio.new_event_loop()
    else:
        loop, _ = loop_dict[token]
    loop_dict[token] = (loop, cur_ts)
    return loop
```

#### `_prepare_conn`
* 透過`get_conn_dict`取得`conn_dict`。
* 接著檢查`token`是否在`conn_dict`中。如果不在的話，呼叫`asyncio.new_event_loop`建立一個新`conn`;如果在的話，從中取出`conn`。
* 透過`conn_dict[token] = (conn, cur_ts)`更新`timestamp`。
* 最後返回`conn`。
```python=
def _prepare_conn(cur_ts: int, token: str) -> EdgeDBCloudConn:
    conn_dict = get_conn_dict()
    if token not in conn_dict:
        conn = EdgeDBCloudConn(**load_st_toml())
    else:
        conn, _ = conn_dict[token]
    conn_dict[token] = (conn, cur_ts)
    return conn
```

#### `run`
為`asyncio`所執行的`coroutine`，其內為一個`try-except*-else`結構。
* 於`try`中，使用`asyncio.TaskGroup`將`app`整體布局的`algo`(即`main` `function`)加入到`task`。請注意，這邊我們用到[[Day26]](https://ithelp.ithome.com.tw/articles/10317778)新學到的技巧，來將`tg`往下傳給`algo`。這麼一來，除了當前這個`task`外，`algo`內也可以新增其它的`task`。
* 於`except* Exception as ex`中，經過`render`後，印出各`Exception`的錯誤資訊。
* 於`else`中，呈現`query`的結果。

```python=
...
tasks = set()

async def run(algo, conn: EdgeDBCloudConn, token: str) -> None:
    top_name = 'top'
    try:
        async with asyncio.TaskGroup() as tg:
            task = tg.create_task(algo(tg, conn, token), name=top_name)
            tasks.add(task)
    except* Exception as ex:
        for exc in ex.exceptions:
            st.warning(f'Exception: {type(exc).__name__}')
            _render_exception(exc)
    else:
        for task in tasks:
            if (task_name := task.get_name()) != top_name:
                st.write(f'task_name: {task_name}')
                _render_result(task.result())
```


#### `main`
為整個app的`layout`。
* 呼叫`_display_sidebar`，建立`sidebar` `element`。
* 呼叫`_get_query_form`，建立`form` `element`。
* 當`form`被`submit`時，呼叫`_create_tasks_for_form`搜集`form`中各項資料並整理後，建立`query` `task`。
* 呼叫`_display_big_red_btn_and_db_calls`，建立一個清除`conn`的小工具。

```python=
...

async def main(tg: asyncio.TaskGroup, conn: EdgeDBCloudConn, token: str) -> None:
    _display_sidebar()
    form = _get_query_form()
    if form.submitted:
        await _create_tasks_for_form(tg, conn, form)
    _display_big_red_btn_and_db_calls(conn, token)
```

## 部署至streamlit cloud
`streamlit cloud`可以部署無限制的`public app`及一個`private app`。

您可以使用`private app`或是使用`public app`加上[authenticator](https://blog.streamlit.io/streamlit-authenticator-part-1-adding-an-authentication-component-to-your-app/)來部署。

部署的過程很簡單，只需完成下列各個選項。所有的`credentials`可以置於`Advanced settings`中，並於app內使用[st.secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)存取。這相當於`local`開發時的`.streamlit/secrets.toml`。

![streamlit-cloud](https://py10wings.jp-osa-1.linodeobjects.com/day28/streamlit-cloud.png)



## 後記
這個project還有非常多可以改進的地方，例如：
* `get_loop_dict`及`get_conn_dict`這樣的方法，在連線數較少時可以使用，但是當連接數較高時，記憶體使用量也會增加不少。或許我們可以將其轉為其它格式，例如`pickle`，然後使用另一個背景程式來定時改動及讀取`pickle`。
* 目前的`Try Free Res`是可以清除掉所有`threshold`大於`3`的`loops`及`conns`。
* `_populate_qry_args`與`_populate_qry_kwargs`需要使用比`eval`與`exec`更安全的處理方式。
* 嘗試其它前端工具。
* 將`mocking`引入`tests`。
* `type annotation`還有很大的進步空間。
* 這個`app`是設計以`asyncio`長期等待`task`，所以db connection不需關閉。但當遇到shutdown時，如何有效關閉所有的connections，還需要好好想想。
* ...


僅管如此，還是學習到了很多，例如：
* 更加了解[EdgeDB-Python](https://www.edgedb.com/docs/clients/python/index)的各種功能。
* 使用新的`asyncio.TaskGroup`與`ExceptionGroup`來處理`asyncio`問題。
* 更加熟悉structural pattern matching的技巧。
* 第一次嘗試將streamlit各個compoment分開，而不是全部擠在`streamlit_app.py`。
* ...

## 備註
註1：`EdgeDB Cloud`已有很好的UI操控介面可以使用，本日內容純屬自我練習之用。

註2：需使用`nest_asyncio.apply`來防止更新`loop`或`conn`時，容易出現的`RuntimeError: Task <Task pending name='Task-xxx' ...> attached to a different loop`。

## Code
[本日程式碼傳送門](https://github.com/jrycw/st-edgedb-cloud-conn)。