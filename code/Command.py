from Base import *
from override import myDatetime as datetime
from Student import Student
import re

class Command:
    def __init__(self, originStr:str, isOutput:bool):
        self.date:datetime = None
        self.type:str = None
        self.bookId:str = None
        self.studentId:str = None
        self.bookCnt:int = None
        self.originStr:str = originStr
        self.start:str = None
        self.end:str = None
        self.orderStu:str = None
        self.isOverdue:bool = None
        self.isSuccess:bool = None
        self.get_type()
        if isOutput:
            self.parse_output()
        else:
            self.parse_input()
        self.check(isOutput)
    
    def check(self, isOutput:bool):
        ans:list
        if isOutput:
            if self.type == MOVE:
                ans = [self.date, self.bookId, self.start, self.end]
            elif self.type == MOVEFOR:
                ans = [self.date, self.bookId, self.start, self.end, self.orderStu]
            elif self.type == RETURNED:
                ans = [self.date, self.isSuccess, self.studentId, self.bookId, self.isOverdue]
            elif self.type == QUERIED:
                ans = [self.date, self.bookId, self.bookCnt]
            elif self.type is not None:
                ans = [self.date, self.isSuccess, self.studentId, self.bookId]
        else:
            if self.type == OPEN or self.type == CLOSE:
                ans = [self.date]
            elif self.type == LOAD:
                ans = [self.bookId, self.bookCnt]
            elif self.type is not None:
                ans = [self.date, self.studentId, self.bookId]
        if None in ans:
            print('parse command failed\n' + self.originStr)
            exit(0)
            
    def get_type(self):
        if self.originStr is None:
            raise TypeError("Can't get type when originStr is None")
        elif re.match(P_OC, self.originStr):
            if 'OPEN' in self.originStr:
                self.type = OPEN
            elif 'CLOSE' in self.originStr:
                self.type = CLOSE
        elif re.match(P_NORM_O, self.originStr) is not None or\
             re.match(P_NORM_I, self.originStr) is not None:
            if 'borrowed' in self.originStr:
                self.type = BORROWED
            elif 'ordered' in self.originStr:
                self.type = ORDERED
            elif 'returned' in self.originStr:
                self.type = RETURNED
            elif 'picked' in self.originStr: 
                self.type = PICKED
            elif 'renewed' in self.originStr:
                self.type = RENEWED
            elif 'donated' in self.originStr:
                self.type = DONATED
            elif 'queried' in self.originStr:
                self.type = QUERIED
        elif re.match(P_QUERY, self.originStr) is not None:
            self.type = QUERIED
        elif re.match(P_LOAD, self.originStr) is not None:
            self.type = LOAD
        elif re.match(P_MOVE, self.originStr) is not None:
            self.type = MOVE
        elif re.match(P_MOVEFOR, self.originStr) is not None:
            self.type = MOVEFOR
        elif re.match(P_RETURNED, self.originStr) is not None:
            self.type = RETURNED
        else:
            myAssert(False, WRONG_INOUT_FORMAT(self.originStr), None)
    
    def parse_input(self): # 解析输入
        if self.type == OPEN or self.type == CLOSE:
            ans = re.match(P_OC, self.originStr)
            self.date = parse_date(ans.group(1))
        elif self.type == LOAD:
            ans = re.match(P_LOAD, self.originStr)
            self.bookId, self.bookCnt = ans.group(1), ans.group(2)
        elif self.type is not None:
            ans = re.match(P_NORM_I, self.originStr)
            self.date, self.studentId, self.bookId =\
                parse_date(ans.group(1)), ans.group(2), ans.group(4)
        else:
            raise TypeError(f'type is none when parse input: {self.originStr}')

    def parse_output(self): # 解析输出
        if self.type == MOVE:
            ans = re.match(P_MOVE, self.originStr)
            self.date, self.bookId, self.start, self.end =\
                parse_date(ans.group(1)), ans.group(2), ans.group(3), ans.group(4)
        elif self.type == MOVEFOR:
            ans = re.match(P_MOVEFOR, self.originStr)
            self.date, self.bookId, self.start, self.end, self.orderStu =\
                parse_date(ans.group(1)), ans.group(2), ans.group(3), ans.group(4), ans.group(5)
        elif self.type == RETURNED:
            ans = re.match(P_RETURNED, self.originStr)
            self.date, self.isSuccess, self.studentId, self.bookId, self.isOverdue =\
                parse_date(ans.group(1)), ans.group(2)[0]=='a', ans.group(3), ans.group(4), ans.group(5)[0]!='n'
        elif self.type == QUERIED:
            ans = re.match(P_QUERY, self.originStr)
            self.date, self.bookId, self.bookCnt =\
                parse_date(ans.group(1)), ans.group(2), int(ans.group(3))
        elif self.type is not None:
            ans = re.match(P_NORM_O, self.originStr)
            self.date, self.isSuccess, self.studentId, self.bookId =\
                parse_date(ans.group(1)), ans.group(2)[0]=='a', ans.group(3), ans.group(5)
        else:
            raise TypeError(f'type is none when parse output: \n{self.originStr}')
    
    def __str__(self):
        if self.type == RETURNED:
            ans = f'{self.date} {"[accept]" if self.isSuccess else "[reject]"} {self.studentId} returned {self.bookId} {"overdue" if self.isOverdue else "not overdue"}\n'
        else:
           ans = self.originStr
        # if self.originStr is not None:
        #     ans = self.originStr
        # elif self.type == LOAD:
        #     ans = f'{self.bookId} {self.bookCnt}'
        # elif self.type == MOVE:
        #     ans = f'{self.date} {self.type} {self.bookId} from {self.start} to {self.end}'
        # elif self.type == MOVEFOR:
        #     ans = f'{self.date} {self.type} {self.bookId} from {self.start} to {self.end} for {self.orderStu}'
        # elif self.type == OPEN or self.type == CLOSE:
        #     ans = f'{self.date} {self.type}'
        # elif self.type == RETURNED:
        #     ans = f'{self.date} {self.isSuccess} {self.studentId} returned {self.bookId} {"overdue" if self.isOverdue else "not overdue"}$'
        # else:
        #     ans = f'{self.date} {self.studentId} {self.type} {self.bookId}'
        # if 'None' in ans:
        #     raise TypeError(f'has None in str(Command): {ans}')
        return ans
        
    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    pass
    # date:datetime = datetime(2024,1,1)
    # open = Command(date, OPEN)
    # print(open)
    # move = Command(**{'start':'ao', 'end':'bs', 'bookId':'B-1000', 'type':'OPEN'})
    # print(move)