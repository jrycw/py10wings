# 04a
from datetime import datetime

now = datetime.now()
datetime_fmt = '%Y-%m-%d_%H:%M:%S'

if __name__ == '__main__':
    now_str = now.strftime(datetime_fmt)
    print(f'{now_str}')  # 2023-09-01_21:14:41
