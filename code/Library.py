import random
from Base import *
from override import myDatetime as datetime
from datetime import timedelta
from Student import Student
from Command import Command

class Library:
    def __init__(self):
        self.students:dict = {} # {studentId: Student}
        self.bs:dict = {} # {bookId: cnt}
        self.bro:list = [] # [bookId]
        self.ao:list = [] # [(bookId, studentId, date)] date代表送来的时间
        self.waitList:list = [] # [(bookId, studentId)]
        self.briTimes:dict = {} # {bookId: cnt}
        self.curDate:datetime = INIT_DATE
        self.nums:dict = {} # {3:3, 4:5} 代表三位数生成到了003 四位数生成到了0005
        self.init_students()

        self.removedBs:list = [] # 书升级后 原书从bs销毁，转存入removedBs，以便查错
        self.testedBorrowTime_notOverdue:dict = {'B':set(),'C':set(),'BU':set(),'CU':set()} # {'B':set(1,2,3)} 代表测试到了B书在借书后1，2，3天归还的情况
        self.testedBorrowTime_overdue:dict = {'B':set(),'C':set(),'BU':set(),'CU':set()} # {'B':set(1,2,3)} 代表测试到了B书在借书后1，2，3天归还的情况
    
    def init_students(self):
        while len(self.students) < INIT_STU_NUM:
            id = self.get_rand_num(8)
            self.students[id] = Student(id)

    def get(self, id) -> Student:
        if id not in self.students: 
            self.students[id] = Student(id)
        return self.students[id]
    
    def query_book(self, cmd:Command) -> int:
        if self.has_left_book(cmd.bookId) == 0:
            return 0
        else:
            return self.bs[cmd.bookId]
    
    def has_left_book(self, bookId:str) -> bool:
        return bookId in self.bs and int(self.bs[bookId]) > 0
    
    def borrow_book(self, cmd:Command) -> bool:
        if self.has_left_book(cmd.bookId) and cmd.bookId[0] != 'A':
            self.bs[cmd.bookId] = int(self.bs[cmd.bookId]) - 1
            if self.get(cmd.studentId).score >= 0 and self.get(cmd.studentId).can_add_book(cmd.bookId):
                self.get(cmd.studentId).add_book(cmd.bookId, cmd.date)
                return True
            else:
                self.bro.append(cmd.bookId)
                return False
        return False
    
    def order_book(self, cmd:Command) -> bool:
        hasOrder:bool = False
        if cmd.bookId[0] == 'B':
            hasOrder = self.has_btype_order_for(cmd.bookId)
        elif cmd.bookId[0] == 'C':
            hasOrder = self.has_order_for(cmd.bookId, cmd.studentId)
        if not hasOrder and self.get(cmd.studentId).score >= 0 and cmd.bookId[1] != 'U' and self.get(cmd.studentId).can_add_book(cmd.bookId):
            self.waitList.append((cmd.bookId, cmd.studentId))
            return True
        return False
    
    def need_upgrade(self, bookId:str) -> bool:
        return bookId in self.briTimes and self.briTimes[bookId] >= 2 

    def is_overdue(self, borrowDate:datetime, bookId:str) -> bool:
        limitDate:timedelta = timedelta(days=get_borrow_limit(bookId)) # 最长借书时间
        return borrowDate + limitDate < self.curDate
    
    def return_book(self, cmd:Command) -> bool:
        if cmd.bookId[1] == 'U':
            self.briTimes[cmd.bookId] = int(self.briTimes[cmd.bookId]) + 1
        self.bro.append(cmd.bookId)
        borrowDate:datetime = self.get(cmd.studentId).remove_book(cmd.bookId) # 借书时间
        limitDate:timedelta = timedelta(days=get_borrow_limit(cmd.bookId)) # 最长借书时间
        cmd.isOverdue = (borrowDate + limitDate < cmd.date)
        cmd.isSuccess = True
        if not cmd.isOverdue:
            self.testedBorrowTime_notOverdue[cmd.bookId.split('-')[0]].add((self.curDate-borrowDate).days)
        else:
            self.testedBorrowTime_overdue[cmd.bookId.split('-')[0]].add((self.curDate-borrowDate).days)
        return cmd.isOverdue
    
    def can_pick_book(self, cmd:Command) -> bool:
        for book in self.ao:
            if book[0:2] == (cmd.bookId, cmd.studentId):
                return True
        return False
    
    def pick_book(self, cmd:Command) -> bool:
        if self.get(cmd.studentId).can_add_book(cmd.bookId):
            for book in self.ao:
                if book[0:2] == (cmd.bookId, cmd.studentId):
                    self.ao.remove(book)
                    self.get(cmd.studentId).add_book(cmd.bookId, cmd.date)
                    return True
        return False
    
    def has_order(self, bookId:str) -> bool:
        return bookId in [i[0] for i in self.waitList] or bookId in [i[0] for i in self.ao]
    
    def has_btype_order_for(self, studentId:str) -> bool:
        return len([i[0] for i in self.waitList if i[0][0] == 'B' and i[0][1] == studentId]) > 0 or\
              len([i[0] for i in self.ao if i[0][0] == 'B' and i[0][1] == studentId]) > 0
    
    def has_order_for(self, bookId:str, studentId:str) -> bool:
        return len([i[0] for i in self.waitList if i[0] == bookId and i[0][1] == studentId]) > 0 or\
              len([i[0] for i in self.ao if i[0] == bookId and i[0][1] == studentId]) > 0
    
    def renew_book(self, cmd:Command) -> bool:
        if self.get(cmd.studentId).score >= 0 and self.get(cmd.studentId).can_renew_book(cmd.bookId, cmd.date)\
            and (self.has_left_book(cmd.bookId) or not self.has_order(cmd.bookId)):
            self.get(cmd.studentId).renew_book(cmd.bookId)
            return True
        return False
    
    def donate_book(self, cmd:Command) -> bool:
        self.bs[cmd.bookId] = 1
        self.briTimes[cmd.bookId] = 0
        return True
    
    def build_books(self, inputList:list):
        for input in inputList:
            cmd:Command = Command(input, False)
            self.bs[cmd.bookId] = cmd.bookCnt
            if cmd.bookId == None:
                print('build books failed\n')
    
    # 数据生成相关------------------------------------------------------------------------------------------------------

    def get_rand_num(self, width:int):
        if width not in self.nums:
            self.nums[width] = 1
        if IS_NEAT:
            self.nums[width] += 1
            return str(self.nums[width]).zfill(width)
        else:
            return str(random.randint(0, 10**width-1)).zfill(width)

    def update_curDate(self, genList:list, delta:int=None) -> datetime: # 若delta是none则随机生成
        if delta is None:
            rand_seed = random.random()
            if rand_seed < 0.5:
                delta = 0
            elif rand_seed < 0.9:
                delta = random.randint(1, 3)
            else:
                delta = random.randint(4, 8)
        if delta != 0:
            genList.append(f'{self.curDate} CLOSE')
            self.curDate += timedelta(days=delta)
            genList.append(f'{self.curDate} OPEN')
        return self.curDate
    
    def get_rand_ubookId(self, type=None): # 
        if type is None:
            type = random.choice(['AU','BU','CU','BU','CU'])
        return f'{type}-{self.get_rand_num(4)}' # 必定成功
    
    def get_rand_bookId(self, hasLeft:bool=False, bookType=None): 
        temp = [i for i in self.bs.items()]
        if bookType is not None:
            temp = [i for i in temp if i[0].split('-')[0] == bookType]
        if hasLeft:# hasLeft=True则尽量生成图书馆有的书
            temp = [i for i in temp if int(i[1]) > 0]
        if len(temp) == 0:
            return self.get_rand_bookId()
        ans = random.choice(temp)
        return ans[0] # 必定成功
    
    def get_rand_studentId(self, canAddBook:str=None, hasBook:bool=False, isNew=False) -> str:
        temp = [i for i in self.students.items()]
        if isNew: # isNew==True时生成新的学生id
            return self.get_rand_num(8)
        if canAddBook is not None: # bookId!=None时则尽量能拿该书的学生
            temp = [i for i in temp if i[1].can_add_book(canAddBook)]
        if hasBook: # hasBook==True时则尽量选有书待还的学生
            temp = [i for i in temp if i[1].has_book()]
        if len(temp) == 0: # 无法满足特殊请求 只能随机选了
            return self.get_rand_studentId()
        ans = random.choice(temp)
        return ans[0]

    def get_rand_book_and_stu_for_pick(self, hasBook:bool=False):
        if len(self.waitList) == 0:
            return None, None
        temp = [i for i in self.waitList]
        if hasBook:
            temp = [i for i in self.waitList if i in [i[0:2] for i in self.ao]]
        if len(temp) == 0:
            return self.get_rand_book_and_stu_for_pick()
        return random.choice(temp)

    def __str__(self):
        # s1 = f'students: {str(self.students)}\n'
        s2 = f'bs: {str(self.bs)}\n'
        s3 = f'bro: {str(self.bro)}\n'
        s4 = f'ao: {str(self.ao)}\n'
        s5 = f'waitList: {str(self.waitList)}\n'
        s6 = f'briTimes: {str(self.briTimes)}\n'
        s7 = f'testedBorrowTime_notOverdue: {str(self.testedBorrowTime_notOverdue)}\n'
        s8 = f'testedBorrowTime_overdue: {str(self.testedBorrowTime_overdue)}\n'
        return s2 + s3 + s4 + s5 + s6 + s7 + s8
    
    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    library = Library()
    print(str(datetime(2023, 1, 1)))
    library.bs['B-0001'] = 2
    library.bs['A-0001'] = 0
    library.bs['C-0001'] = 4
    # for i in range(10):
    #     print(library.get_rand_bookId(False))

    stu1 = Student('00000001')
    stu1.books['B'] = {'B-0001': datetime(2023, 1, 1)}
    stu1.books['C'] = {'C-0002': datetime(2023, 1, 1)}
    stu2 = Student('00000002')
    stu2.books['B'] = {'B-0003': datetime(2023, 1, 1)}
    stu2.books['C'] = {'C-0004': datetime(2023, 1, 1)}
    library.students['00000001'] = stu1
    library.students['00000002'] = stu2
    for i in range(10):
        print(library.get_rand_studentId('C-0002'))