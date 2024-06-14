import random
from Base import *
from override import myDatetime as datetime
from datetime import timedelta
from Library import Library
from Command import Command

def gen_first_ops(library:Library, account:int):
    genList = []
    genList.append(str(account))
    while len(library.bs) < account:
        bookId = f'{random.choice(["A", "B", "C"])}-{library.get_rand_num(4)}'
        if bookId not in library.bs:
            copies:int = random.randint(0, MAX_BOOK_COPY)
            library.bs[bookId] = copies
            genList.append(f'{bookId} {copies}')
    return genList

def gen_new_ops(library:Library, testMode:str) -> list:
    ans:list
    if testMode == MODE_RAND:
        ans = test_rand(library)
    elif testMode == MODE_OVERDUE:
        ans = test_overdue(library)
    myAssert(ans is not None, 'gen_new_op failed got None', None)
    myAssert(len(ans) != 0, 'gen_new_op failed got len(ans) == 0', None)
    return ans

def test_rand(library:Library) -> list:
    rand_seed = random.random()
    genList = []
    if rand_seed < 0.15:
        genList += gen_borrows(random.randint(1, 3), library)
        library.update_curDate(genList)
    elif rand_seed < 0.3:
        genList += gen_return(library)
        library.update_curDate(genList)
    elif rand_seed < 0.5:
        genList += gen_orders(random.randint(1, 3), library)
        library.update_curDate(genList)
    elif rand_seed < 0.7:
        genList += gen_pick(library)
        library.update_curDate(genList)
    elif rand_seed < 0.9:
        genList += gen_renew(library)
        library.update_curDate(genList)
    elif rand_seed < 1:
        genList += gen_donates(random.randint(1, 3), library)
        library.update_curDate(genList)
    if len(genList) == 0:
        genList += gen_borrows(1, library)
    return genList

def get_untested_borrowTime(library:Library):
    for student in library.students.items():
        for oneTypebooks in student[1].books.items():
            for book in oneTypebooks[1].items():
                borrowDates = (library.curDate - book[1]).days
                bookType = book[0].split('-')[0]
                if library.is_overdue(book[1], book[0]) and \
                    borrowDates not in library.testedBorrowTime_overdue[bookType] or\
                   not library.is_overdue(book[1], book[0]) and \
                    borrowDates not in library.testedBorrowTime_notOverdue[bookType]:
                    return book[0], student[0] # 需要return
                if random.random() < 0.7:
                    return 'can renew', None
    return None, None

def test_overdue(library:Library) -> list:
    # 测试不同种类的书在临近还书日期时还书，和临近续借规定日期附近续借
    genList = []
    bookId, studentId = get_untested_borrowTime(library)
    if bookId is not None:
        genList += gen_return(library, studentId=studentId, bookId=bookId)
    elif studentId is not None:
        genList += gen_renew(library)
    if genList is None or len(genList) == 0:
        for bookType in ['B', 'C', 'BU', 'CU']:
            genList += gen_borrows(1, library, bookType=bookType, hasLeft=True,\
                                    canAddBook=True, newStudent=True)
    genList += gen_donates(1, library, newStudent=True) if random.random() < 0.4 else []
    library.update_curDate(genList, delta=1)
    return genList

    
def gen_borrows(account:int, library:Library, bookType=None, hasLeft=False, canAddBook=False, newStudent=False) -> list:
    ans = []
    for i in range(account):
        bookId = library.get_rand_bookId(hasLeft=hasLeft, bookType=bookType)
        studentId = library.get_rand_studentId(isNew=newStudent, canAddBook=bookId if canAddBook else None)
        ans.append(f'{library.curDate} {studentId} borrowed {bookId}')
    return ans # 必定成功

def gen_return(library:Library, studentId=None, bookId=None) -> list:
    ans = []
    studentId = library.get_rand_studentId(hasBook=True) if studentId is None else studentId
    bookId = library.get(studentId).get_rand_book() if bookId is None else bookId
    if bookId is not None: 
        ans.append(f'{library.curDate} {studentId} returned {bookId}')
    return ans #可能会失败！！！# 所有学生都两手空空 没书可还

def gen_orders(account:int, library:Library) -> list :
    ans = []
    for i in range(account):
        bookId = library.get_rand_bookId()
        studentId = library.get_rand_studentId()
        ans.append(f'{library.curDate} {studentId} ordered {bookId}')
    return ans # 必定成功

def gen_pick(library:Library) -> list:
    ans = []
    bookId, studentId = library.get_rand_book_and_stu_for_pick(hasBook=True)
    if bookId is not None:
        ans.append(f'{library.curDate} {studentId} picked {bookId}')
    return ans  #可能会失败！！！# waitlist 为空

def gen_renew(library:Library) -> list:
    ans = []
    studentId = library.get_rand_studentId(hasBook=True)
    bookId = library.get(studentId).get_rand_book()
    if bookId is not None: 
        ans.append(f'{library.curDate} {studentId} renewed {bookId}')
    return ans #可能会失败！！！# 所有学生都两手空空 没书可续借

def gen_donates(account:int, library:Library, newStudent=False) -> list:
    ans = []
    for i in range(account):
        studentId = library.get_rand_studentId(isNew=newStudent)
        bookId = library.get_rand_ubookId()
        ans.append(f'{library.curDate} {studentId} donated {bookId}')
    return ans #必定成功

if __name__ == '__main__':
    library = Library()
    with open("gen.txt", "w") as f:
        f.writelines(gen_first_ops(library, 10))
    
