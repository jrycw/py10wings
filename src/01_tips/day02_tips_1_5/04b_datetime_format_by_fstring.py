# 04b
from datetime import datetime

now = datetime.now()
datetime_fmt = '%Y-%m-%d_%H:%M:%S'

if __name__ == '__main__':
    print(f'{now:{datetime_fmt}}')  # 2023-09-01_21:14:41
