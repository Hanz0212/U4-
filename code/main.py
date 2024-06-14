import os
import subprocess
from time import sleep
from tqdm import tqdm

from func import *
from generator import *
from Base import *
from checker import *
from Library import Library
# def reset():
#     Base.books = {}  # 已上架的书，形如 <book_id, stock>，key永远不会被清空
#     Base.bro = [] # 借还台的书，形如 [book_id1, book_id2]
#     Base.ao = {} # 预约台的书，形如 <student_id, [(book_id1, time1), (bookk_id2, time2)]> time代表送来的时间
#     Base.wait = {} # 待送至预约台的书，形如 <student_id, [(book_id1, time1), (bookk_id2, time2)]>time代表放到wait里的时间（order的时间）
#     Base.students = {}   # 学生，形如 <id, {'B': book_set(), 'C': book_set()}>
#     Base.cur_date = datetime(2024, 5, 26).date()
#     # 指令列表
#     Base.data_list = []
#     # 辅助变量
#     Base.num_gen = rand_num() # 用于生成整齐随机数
#     Base.gen_times_now = 0
#     # base.borrow_cnt = 0
#     # base.borrow_success_cnt = 0
#     # base.pick_cnt = 0
#     # base.pick_success_cnt = 0
#     if Base.STOP :
#         exit(0)


def run(testMode, JAR_PATH=JAR_PATH):
    # reset()
    open(OUT_PATH, 'w').truncate() 
    open(IN_PATH, 'w').truncate()
    open(APP_PATH, 'w').truncate() 
    open(MER_PATH, 'w').truncate() 
    library:Library = Library()
    cmd = ["java", "-jar", JAR_PATH]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    inputList = gen_first_ops(library, INIT_BOOK_NUM) # 获取最初的输入
    outputList = []
    left = 0 # 还剩多少行未输出
    genCnt = 0 # 当前已经生成了几次数据
    pipe_in_list(inputList, p.stdin, IN_PATH) # 将初始输入传入管道，并输出到IN_PATH

    print(os.getcwd())
    with open(OUT_PATH, 'a+') as fout:
        while True:
            if genCnt == GEN_TIMES_MAX:
                break
            elif left == 0 : # 获得了上次生成的输入所对应的所有输出
                check(inputList, outputList, library) 
                if STOP:
                    break
                inputList = gen_new_ops(library, testMode)
                # print(inputList)
                outputList = []
                genCnt += 1
                pipe_in_list(inputList, p.stdin, APP_PATH) # 将新生成的输入传进管道
                left = len(inputList) # 还剩多少行未输出
            else:
                output = pipe_out(p.stdout, fout) # 获取一行输出
                if output.strip().isdigit(): # move指令 剩余待输出行数增加
                    left = left + int(output)
                left = left - 1
                outputList.append(output) 
    
    save_msg(str(library))
    p.kill()

if __name__ == "__main__":
    os.chdir(RUN_PATH) # 进入工作目录
    for i in tqdm(range(100)):
        run(MODE_RAND)
    


