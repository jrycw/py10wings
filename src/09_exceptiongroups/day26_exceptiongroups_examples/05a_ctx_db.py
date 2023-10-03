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
