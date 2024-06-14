import re
from datetime import datetime
class myDatetime(datetime):
    def __str__(self):
        return f'[{str(self.year).zfill(4)}-{str(self.month).zfill(2)}-{str(self.day).zfill(2)}]'
    def __repr__(self):
        return f'[{str(self.year).zfill(4)}-{str(self.month).zfill(2)}-{str(self.day).zfill(2)}]'

if __name__ == '__main__':
    print(str(myDatetime(2023, 1, 1)))