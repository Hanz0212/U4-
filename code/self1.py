import os

from func import *
from Base import *
from checker import *
from Library import Library



if __name__ == '__main__':
    os.chdir(RUN_PATH) # 进入工作目录
    merge_file(IN_PATH, APP_PATH, MER_PATH) # 将初始输入和根据输出新增的输入合并到新文件
    cmd = ["java", "-jar", JAR_PATH, "<", MER_PATH, ">", OUT_PATH]
    os.system(" ".join(cmd))
    input = open(MER_PATH, 'r').readlines()
    output = open(OUT_PATH, 'r').readlines()
    library = Library()
    check(input, output, library)
    print("over")