import re
import sys
from override import myDatetime as datetime
from func import merge_file

RUN_PATH = r'D:/python_code/hw13/'
OUT_DIR = r'output/'
MUTUAL_OUT_DIR = r'output/mutual_out/'
SELF_OUT_DIR = r'output/self_out/'
JAR_PATH = r"oohomework_2024_21375212_hw_1515.jar"

IN_PATH = OUT_DIR + r"in.txt"
OUT_PATH = OUT_DIR + r"out.txt"
APP_PATH = OUT_DIR + r"append.txt"
MER_PATH = OUT_DIR + r"merge.txt"
LIBRARY_PATH = OUT_DIR + r"library.txt"

# 参数设置
INIT_DATE = datetime(2024, 5, 31)
IS_NEAT = True
GEN_TIMES_MAX = 2000

INIT_BOOK_NUM = 50
MAX_BOOK_COPY = 5
INIT_STU_NUM = 100
STOP = False # 程序或评测机出现问题，停止标记
# 数据生成模式
MODE_RAND = 'RAND'
MODE_OVERDUE = 'DATELIMIT'
TEST_MODE = [MODE_RAND, MODE_OVERDUE]
# 图书馆信息

OPEN = 'OPEN'
CLOSE = 'CLOSE'
LOAD = 'LOAD'
MOVE = 'MOVE'
MOVEFOR = 'MOVEFOR'
QUERIED = 'QUERIED'
RETURNED = 'RETURNED'
BORROWED = 'BORROWED'
ORDERED = 'ORDERED'
PICKED = 'PICKED'
RENEWED = 'RENEWED'
DONATED = 'DONATED'

P_DATE = '(\[\d{4}-\d{2}-\d{2}\])'
P_ISSUCCESS = '\[(accept|reject)\]'
P_STU = '(\d{8})'
P_BOOKID = '([A|B|C]U?-\d{4})'
P_BOOKCNT = '([0-9]|10)'
P_LOC =  '(bs|bro|ao|bdc)'
P_OCOP = '(OPEN|CLOSE)'
P_NORMOP = '(borrowed|ordered|picked|renewed|donated|queried|returned)'
P_OVERDUE = '(not overdue|overdue)'

P_LOAD = f'^{P_BOOKID} {P_BOOKCNT}$'
P_OC = f'^{P_DATE} {P_OCOP}$'
P_RETURNED = f'^{P_DATE} {P_ISSUCCESS} {P_STU} returned {P_BOOKID} {P_OVERDUE}$'
P_MOVE = f'^{P_DATE} move {P_BOOKID} from {P_LOC} to {P_LOC}$'
P_MOVEFOR = f'^{P_DATE} move {P_BOOKID} from {P_LOC} to {P_LOC} for {P_STU}$'
P_NORM_O = f'^{P_DATE} {P_ISSUCCESS} {P_STU} {P_NORMOP} {P_BOOKID}$'
P_NORM_I = f'^{P_DATE} {P_STU} {P_NORMOP} {P_BOOKID}$'
P_QUERY = f'^{P_DATE} {P_BOOKID} {P_BOOKCNT}$'

def parse_date(str:str) -> datetime:
    ans = re.match('\[(\d{4})-(\d{2})-(\d{2})\]', str)
    return datetime(int(ans.group(1)), int(ans.group(2)), int(ans.group(3)))

def updated_bookId(bookId:str):
    newType:str = bookId[0]
    id = bookId.split('-')[1]
    return f'{newType}-{id}'

def save_msg(msg:str):
    merge_file(IN_PATH, APP_PATH, MER_PATH)
    with open(LIBRARY_PATH, 'w') as f:
        f.write(msg)

def myAssert(flag, str, library:str) :
    global STOP
    if not flag and not STOP :
        print(str, file=sys.stderr)
        STOP = True
        save_msg(library)
        exit()

def get_borrow_limit(bookId:str) -> int:
    bookType:str = bookId.split('-')[0]
    if bookType == 'B' : return 30
    elif bookType == 'C' : return 60
    elif bookType == 'BU' : return 7
    elif bookType == 'CU' : return 14
    else : myAssert(False, f'Invalid bookId:{bookId}', None)

# 整理
def NO_NUM_AFTER_OPEN_OR_CLOSE(output):
    return f' expected a num but we got {output}' + 'need tidy after open/close, or you need to print 0'

def LESS_NUM_AFTER_OPEN_OR_CLOSE(output, expectedNum):
    return f' tidy not enough, in this case we expect at least tidy {expectedNum} times,'\
            f'but we got {output}'

def TIDY_WRONG_AFTER_OPEN_OR_CLOSE(output):
    return f' this move is not allowed:{output}' + 'because'

def TIDY_NOT_FINISH_AFTER_OPEN_OR_CLOSE(output, expectedNum):
    return f' tidy not enough, in this case we expect at least tidy {expectedNum} times:'\
            f'but we got {output}'

def MOVE_WITHOUT_FOR(output):
    return f' move book to ao without \'for whom\' in the end:\n{output}'

def WRONG_FOR_WHEN_MOVE(output):
    return f' end with \'for\' but the dst is not ao:\n{output}'

def MOVE_UNUBOOK_TO_BDC(output):
    return f' move \'not utype book\' to bdc:\n{output}'

def MOVE_UBOOK_TO_BS(output):
    return f' move \'utype book\' to bs:\n{output}'

def NO_SUCH_BOOK_IN_BRO(output, bro):
    return f' no such book in bro:\n{output}bro: {bro}'

def NO_REASON_MOVE_BOOK_FROM_AO(output):
    return f' cant move this book in ao\nbecause its not overdue yet or no such book in ao:\n{output}'

def MOVE_WITHOUT_ORDER(output):
    return f' move book when no order before:\n{output}'

def ILLEGAL_MOVE(output):
    return f' such move is not allowed:\n{output}\n'\
        'legal moves are as follows:\n'\
        'ao->bs ao->bdc bro->bs bro->bdc bs->ao'

def HAVE_BOOK_IN_BRO_AFTER_OPEN(output, bro):
    return f' still have book in bro after open:\n{output}bro: {bro}'

def HAVE_OVERDUE_BOOK_IN_AO_AFTER_OPEN(output):
    return f' still have overdue book in ao after open:\n{output}'

def MOVE_ALREADY_UPDATED_BOOK(output):
    return f'this book has already been updated after last tidy: \n{output}'

# 借书问题
def BORROW_ATYPE_BOOK(output):#
    return f' cant borrrow A type book:\n{output}'

def NO_BOOK_LEFT_IN_BS(output):#
    return f' no book left in bookshelf:\n{output}'

def NO_REASON_REJECT_BORROW(output):#
    return f' no reason reject borrow:\n{output}'

def NO_REASON_ACCEPT_BORROW(output):
    return f' no reason accept borrow:\n{output}'

def BORROW_WHEN_SCORE_LOWER_THEN_ZERO(output):
    return f' cant borrow book when score is lower than 0: \n{output}'

# 还书问题
def RETURN_BOOK_FAILED(output):#
    return f' return book should always accept:\n{output}'

def OVERDUE_JUDGE_FAILED(output, expected):#
    return f' overdue judge failure, we got\n{output}but we expected:\n{expected}'

# 预定问题
def ORDER_A_BOOK(output):#
    return f' cant order A type book:\n{output}'

def ORDER_U_BOOK(output):
    return f' cant order U type book:\n{output}'

def NO_REASON_REJECT_ORDER(output):#
    return f' no reason reject order:\n{output}'

def NO_REASON_ACCEPT_ORDER(output):
    return f' no reason accept order:\n{output}'

def ORDER_WHEN_SCORE_LOWER_THEN_ZERO(output):
    return f' cant order book when score is lower than 0: \n{output}'

def ORDER_WHEN_HAS_ORDER_B(output):
    return f' cant order book when already has btype book order:\n{output}'

def ORDER_WHEN_HAS_ORDER_C_COPY(output):
    return f' cant order book when already has ctype book copy order:\n{output}'

# 取书问题
def PICK_WHEN_NOT_BOOK_IN_AO(output):#
    return f' no such book in ao when pick:\n{output}'

def NO_REASON_REJECT_PICK(output):#
    return f' no reason reject pick:\n{output}'

def NO_REASON_ACCEPT_PICK(output):
    return f' no reason accept pick:\n{output}'

# 查询问题
def WRONG_NUM_WHEN_QUERY(output, expected):
    return f' query error, we got :\n{output}\nbut we expect \n{expected}'

# 续借问题
def RENEW_AT_WRONG_DATE(output):
    return f' cant renew book now because is too late/early :\n{output}'

def RENEW_WHEN_BS_DONT_HAVE_AND_HAS_ORDER(output):
    return f' cant renew book when bs dont have this book and someone else had orderd this book:\n{output}'

def NO_REASON_REJECT_RENEW(output):
    return f' no reason reject renew book: \n{output}'

def RENEW_UTYPE_BOOK(output):
    return f' cant renew utype book: \n{output}'

def RENEW_WHEN_SCORE_LOWER_THEN_ZERO(output):
    return f' cant renew book when score is lower than 0: \n{output}'

# 捐赠问题
def DONATE_BOOK_FAILED(output):
    return f'donate book should always accept: \n{output}'

# 漂流角相关
def NOT_UPDATE_WHEN_RESET(output):
    return f' not update when reset:\n{output}'

# 通用
def DATE_NOT_EQUAL(output, expected):
    return f' date error, we got \n{output}\nbut we expect \n{expected}'

def STUDENTID_NOT_EQUAL(output, expected):
    return f' student_id error, we got \n{output}\nbut we expect \n{expected}'

def BOOKID_NOT_EQUAL(output, expected):
    return f' bookId error, we got \n{output}\nbut we expect \n{expected}'

def TYPE_NOT_EQUAL(output, expected):
    return f' type error, we got \n{output}\nbut we expect \n{expected}'

def ALREADY_HAVE_B_BOOK(output):
    return f' already have B type book:\n{output}' 

def ALREADY_HAVE_BU_BOOK(output):
    return f' already have BU type book:\n{output}' 

def ALREADY_HAVE_C_BOOK_COPY(output):
    return f' already have C type book copy:\n{output}'

def ALREADY_HAVE_CU_BOOK_COPY(output):
    return f' already have CU type book copy:\n{output}'

def WRONG_INOUT_FORMAT(output):
    return f' wrong input/output format when get type:\n{output}'