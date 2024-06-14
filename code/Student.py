import random
from Base import *
from override import myDatetime as datetime
from datetime import timedelta

class Student :
    def __init__(self, id:str):
        self.score:int = 10
        self.id:str = id
        self.books:dict = {'B':{}, 'C':{}, 'BU':{}, 'CU':{}} # {'B':{B-0000:2024-5-1}, 'C':{C-0000:2024-5-2}}

    def can_add_book(self, bookId:str) -> bool:
        bookType:str = bookId.split('-')[0]
        if bookType[0] == 'A' :
            return False
        elif bookType[0] == 'B' : # B or BU
            return len(self.books[bookType]) == 0
        elif bookType[0] == 'C' : # C or CU
            return bookId not in self.books[bookType]
        else : 
            raise TypeError(f'in can_add_book\nInvalid bookId:{bookId}')
    
    def can_renew_book(self, bookId:str, curDate:datetime) -> bool:
        bookType:str = bookId.split('-')[0]
        borrowDate:datetime = self.books[bookType][bookId]
        latestDate = borrowDate + timedelta(days=get_borrow_limit(bookId))
        earliestDate = latestDate - timedelta(days=5)
        return curDate > earliestDate and curDate <= latestDate and bookId[1] != 'U'

    def add_book(self, bookId:str, date:datetime):
        bookType:str = bookId.split('-')[0]
        self.books[bookType][bookId] = date
    
    def remove_book(self, bookId:str) -> datetime:
        bookType:str = bookId.split('-')[0]
        date:datetime = self.books[bookType][bookId]
        del self.books[bookType][bookId]
        return date
    
    def renew_book(self, bookId:str):
        # print(bookId, self.books[bookId.split('-')[0]][bookId], self.books[bookId.split('-')[0]][bookId] + timedelta(days=30))
        self.add_book(bookId, self.remove_book(bookId) + timedelta(days=30))
    
    def __str__(self):
        return self.id
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Student):
            raise TypeError('==运算要求目标是Student')
        return self.id == other.id
    
    # 数据生成相关------------------------------------------------------------------------------------------------------

    def has_book(self) -> bool:
        return [i for i in self.books.values() if len(i) > 0] != []

    def get_rand_book(self, type:str=None) -> str: # 尽量选有书的type
        if not self.has_book():
            return None # 可能会失败！！！！如果学生没有书的话
        elif type is not None and len(self.books[type]) == 0: 
            return self.get_rand_book()
        elif type is not None:
            pass
        else:
            type = random.choice([i[0] for i in self.books.items() if len(i[1]) > 0])
        return random.choice(list(self.books[type]))
        

if __name__ == '__main__':
    # pass
    student = Student('00000001')
    student.add_book('B-0001', datetime(2024, 1, 1))
    # student.can_renew_book('B-1101', datetime(2024,1,1))
    print(student.has_book())