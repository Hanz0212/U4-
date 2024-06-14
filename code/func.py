# 向管道输入一个字符串，若file不空，同时写进file
import os


def pipe_in(s:str, pipe, file=None) :
    s:str = str(s) + '\n'
    pipe.write(s.encode('utf-8'))
    pipe.flush()
    if file is not None :
        file.write(s)

# 从管道读取一行字符串，若file不空，同时写进file
def pipe_out(pipe, file=None) :
    str = pipe.readline().decode('utf-8').strip() + '\n'
    if file is not None :
        file.write(str)
    return str

# 向管道输入一组字符串，若file不空，同时写进file
def pipe_in_list(strList:list, pipe, file=None) :
    if file is not None :
        with open(file, 'a+') as f:
            for str in strList :
                pipe_in(str, pipe, f)

# 合并两个文件
def merge_file(file1:str, file2:str, file3:str) :
    with open(file1, "r") as f1 :
        txt1 = f1.read()
    with open(file2, "r") as f2 :
        txt2 = f2.read()
    with open(file3, "w") as f3 :
        f3.write(txt1)
        f3.write(txt2)

def get_jar_names():
    # 获取指定目录下的所有指定后缀的文件名 
    ans=[]
    f_list = os.listdir(os.curdir)#返回文件名
    for i in f_list:
        # os.path.splitext():分离文件名与扩展名
        if os.path.splitext(i)[1] == '.jar':
            ans.append(i.split('.')[-2])
    return ans
