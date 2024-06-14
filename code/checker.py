from Base import *
from override import myDatetime as datetime
from datetime import timedelta
from Student import Student
from Command import Command
from Library import Library

def check(inputList:list, outputList:list, library:Library):
    pi = po = 0
    if str(inputList[0]).strip().isdigit(): 
        library.build_books(inputList[1:1+int(inputList[0])])
        pi = 1 + int(inputList[0].strip())
    while pi < len(inputList):
        input:str = inputList[pi]
        output:str = outputList[po]
        if 'OPEN' in input or 'CLOSE' in input:
            myAssert(output.strip().isdigit(), NO_NUM_AFTER_OPEN_OR_CLOSE, str(library))
            checkMove(input, outputList[po+1:po+1+int(output)], library)
            po += int(output)
        elif 'borrowed' in input:
            checkBorrow(input, output, library)
        elif 'returned' in input:
            checkReturn(input, output, library)
        elif 'ordered' in input:
            checkOrder(input, output, library)
        elif 'picked' in input:
            checkPick(input, output, library)
        elif 'renewed' in input:
            checkRenew(input, output, library)
        elif 'donated' in input:
            checkDonate(input, output, library)
        elif 'queried' in input:
            checkQuery(input, output)
        else:
            myAssert(False, f"Unknown input type: {input}\n", str(library))
        pi += 1
        po += 1
        
    return None

def checkMove(input:str, outputList:list, library:Library) : # input含open或close，output为一些列move
    # ao->bs ao->bdc bro->bs bro->bdc bs->ao
    cmdIn = Command(input, False)
    for output in outputList:
        cmdOut = Command(output, True)
        myAssert(cmdOut.date == cmdIn.date, DATE_NOT_EQUAL(cmdOut, cmdIn), str(library))
        myAssert(cmdOut.bookId not in library.removedBs, MOVE_ALREADY_UPDATED_BOOK(cmdOut), str(library))
        if cmdOut.type == MOVE: 
            myAssert(cmdOut.end != "ao", MOVE_WITHOUT_FOR(cmdOut), str(library))
        else:                   
            myAssert(cmdOut.end == "ao", WRONG_FOR_WHEN_MOVE(cmdOut), str(library))
        myAssert(not(cmdOut.end == "bdc" and cmdOut.bookId[1] != 'U'), MOVE_UNUBOOK_TO_BDC(cmdOut), str(library))
        myAssert(not(cmdOut.end == "bs" and cmdOut.bookId[1] == 'U') or library.need_upgrade(cmdOut.bookId), MOVE_UBOOK_TO_BS(cmdOut), str(library))
        if cmdOut.start == "bro" and (cmdOut.end == "bs" or cmdOut.end == "bdc"):
            myAssert(cmdOut.bookId in library.bro, NO_SUCH_BOOK_IN_BRO(cmdOut, str(library.bro)), str(library))
            library.bro.remove(cmdOut.bookId)
            if library.need_upgrade(cmdOut.bookId):
                myAssert(cmdOut.end == "bs", NOT_UPDATE_WHEN_RESET(cmdOut), str(library))
                del library.bs[cmdOut.bookId] # 销毁原书
                library.removedBs.append(cmdOut.bookId)
                library.bs[updated_bookId(cmdOut.bookId)] = 1 # 建立新书
            else:
                library.bs[cmdOut.bookId] += 1
        elif cmdOut.start == "ao" and (cmdOut.end == "bs" or cmdOut.end == "bdc"):
            date:datetime = cmdOut.date if cmdIn.type == OPEN else cmdOut.date + timedelta(days=1)
            validBooks = [i for i in library.ao if i[0]==cmdOut.bookId and i[2]+timedelta(days=5)<=date]
            myAssert(len(validBooks) != 0, NO_REASON_MOVE_BOOK_FROM_AO(cmdOut), str(library))
            library.ao.remove(validBooks[0])
            library.bs[cmdOut.bookId] += 1
        elif cmdOut.start == "bs" and cmdOut.end == "ao":
            myAssert(library.has_left_book(cmdOut.bookId), NO_BOOK_LEFT_IN_BS(cmdOut), str(library))
            library.bs[cmdOut.bookId] = int(library.bs[cmdOut.bookId]) - 1
            myAssert((cmdOut.bookId, cmdOut.orderStu) in library.waitList, MOVE_WITHOUT_ORDER(cmdOut), str(library))
            library.waitList.remove((cmdOut.bookId, cmdOut.orderStu))
            library.ao.append((cmdOut.bookId, cmdOut.orderStu, cmdOut.date))
        else : 
            myAssert(False, ILLEGAL_MOVE(cmdOut), str(library))
    if cmdIn.type == OPEN:
        myAssert(len(library.bro) == 0, HAVE_BOOK_IN_BRO_AFTER_OPEN(cmdIn, str(library.bro)), str(library))
        date:datetime = cmdIn.date if cmdIn.type == OPEN else cmdIn.date + timedelta(days=1)
        myAssert(len([i for i in library.ao if i[2]+timedelta(days=5)<=date]) == 0, HAVE_OVERDUE_BOOK_IN_AO_AFTER_OPEN(outputList), str(library))

def checkSame(cmdIn:Command, cmdOut:Command, library:Library):
    myAssert(cmdIn.date == cmdOut.date, DATE_NOT_EQUAL(cmdOut, cmdIn), str(library))
    myAssert(cmdIn.type == cmdOut.type, TYPE_NOT_EQUAL(cmdOut, cmdIn), str(library))
    myAssert(cmdIn.studentId == cmdOut.studentId, STUDENTID_NOT_EQUAL(cmdOut, cmdIn), str(library))
    myAssert(cmdIn.bookId == cmdOut.bookId, BOOKID_NOT_EQUAL(cmdOut, cmdIn), str(library))

def checkOwnedBook(cmd:Command, library:Library):
    bookType:str = (cmd.bookId.split('-'))[0]
    myAssert(len(library.get(cmd.studentId).books['B']) == 0 or bookType != 'B', ALREADY_HAVE_B_BOOK(cmd), str(library))
    myAssert(len(library.get(cmd.studentId).books['BU']) == 0 or bookType != 'BU', ALREADY_HAVE_BU_BOOK(cmd), str(library))
    myAssert(cmd.bookId not in library.get(cmd.studentId).books['C'] or bookType != 'C', ALREADY_HAVE_C_BOOK_COPY(cmd), str(library))
    myAssert(cmd.bookId not in library.get(cmd.studentId).books['CU'] or bookType != 'CU', ALREADY_HAVE_CU_BOOK_COPY(cmd), str(library))

def checkBorrow(input:str, output:str, library:Library) :
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    checkSame(cmdIn, cmdOut, library)
    if cmdOut.isSuccess:
        myAssert(cmdIn.bookId[0] != 'A', BORROW_ATYPE_BOOK(cmdOut), str(library))
        myAssert(library.has_left_book(cmdIn.bookId), NO_BOOK_LEFT_IN_BS(cmdOut), str(library))
        checkOwnedBook(cmdOut, library)
        myAssert(library.get(cmdIn.studentId).score >= 0, BORROW_WHEN_SCORE_LOWER_THEN_ZERO(cmdOut), str(library))
        myAssert(library.borrow_book(cmdIn), NO_REASON_ACCEPT_BORROW(cmdOut), str(library))
    else : 
        myAssert(not library.borrow_book(cmdIn), NO_REASON_REJECT_BORROW(cmdOut), str(library))

def checkReturn(input:str, output:str, library:Library) :
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    checkSame(cmdIn, cmdOut, library)
    myAssert(cmdOut.isSuccess, RETURN_BOOK_FAILED(cmdOut), str(library))
    myAssert(cmdOut.isOverdue == library.return_book(cmdIn), OVERDUE_JUDGE_FAILED(cmdOut, cmdIn), str(library))

def checkOrder(input:str, output:str, library:Library) :
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    checkSame(cmdIn, cmdOut, library)
    bookType:str = (cmdIn.bookId.split('-'))[0]
    if cmdOut.isSuccess :
        myAssert(bookType[0] != 'A', ORDER_A_BOOK(cmdOut), str(library))
        myAssert(len(bookType) == 1, ORDER_U_BOOK(cmdOut), str(library))
        checkOwnedBook(cmdOut, library)
        myAssert(library.get(cmdIn.studentId).score >= 0, ORDER_WHEN_SCORE_LOWER_THEN_ZERO(cmdOut), str(library))
        myAssert(not bookType[0] == 'B' or not library.has_btype_order_for(cmdIn.studentId),\
                  ORDER_WHEN_HAS_ORDER_B(cmdOut), str(library))
        myAssert(not bookType[0] == 'C' or not library.has_order_for(cmdIn.bookId, cmdIn.studentId),\
                  ORDER_WHEN_HAS_ORDER_C_COPY(cmdOut), str(library))
        myAssert(library.order_book(cmdIn), NO_REASON_ACCEPT_ORDER(cmdOut), str(library))
    else :
        myAssert(not library.order_book(cmdIn), NO_REASON_REJECT_ORDER(cmdOut), str(library))

def checkPick(input:str, output:str, library:Library) :
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    checkSame(cmdIn, cmdOut, library)    
    if cmdOut.isSuccess :
        checkOwnedBook(cmdOut, library)
        myAssert(library.can_pick_book(cmdOut), PICK_WHEN_NOT_BOOK_IN_AO(cmdOut), str(library))
        myAssert(library.pick_book(cmdOut), NO_REASON_ACCEPT_PICK(cmdOut), str(library))
    else :
        myAssert(not library.pick_book(cmdOut), NO_REASON_REJECT_PICK(cmdOut), str(library))

def checkRenew(input:str, output:str, library:Library) :
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    checkSame(cmdIn, cmdOut, library)  
    if cmdOut.isSuccess :
        myAssert(library.get(cmdOut.studentId).can_renew_book(cmdOut.bookId, cmdOut.date), RENEW_AT_WRONG_DATE(cmdOut), str(library))
        myAssert(library.has_left_book(cmdOut.bookId) or not library.has_order(cmdOut.bookId), RENEW_WHEN_BS_DONT_HAVE_AND_HAS_ORDER(cmdOut), str(library))
        myAssert(cmdOut.bookId[1] != 'U', RENEW_UTYPE_BOOK(cmdOut), str(library))
        myAssert(library.get(cmdIn.studentId).score >= 0, RENEW_WHEN_SCORE_LOWER_THEN_ZERO(cmdOut), str(library))
        library.renew_book(cmdOut)
    else:
        myAssert(not library.renew_book(cmdOut), NO_REASON_REJECT_RENEW(cmdOut), str(library))

def checkDonate(input:str, output:str, library:Library):
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    checkSame(cmdIn, cmdOut, library) 
    myAssert(cmdOut.isSuccess, DONATE_BOOK_FAILED(cmdOut), str(library))
    library.donate_book(cmdOut)

def checkQuery(input:str, output:str, library:Library) :
    cmdIn = Command(input, False)
    cmdOut = Command(output, True)
    expected:int = library.query_book(cmdIn)
    myAssert(expected == cmdOut.bookCnt, WRONG_NUM_WHEN_QUERY(cmdOut, expected), str(library))
    pass


if __name__ == '__main__':
    library = Library()
    # checkBorrow("[2024-01-05] 22370001 borrowed B-0000", "[2024-01-05] [accept] 22370001 borrowed B-0000", library)
    checkQuery("[2024-01-30] 22370002 queried B-0000", "[2024-01-30] B-0000 1", library)
    pass