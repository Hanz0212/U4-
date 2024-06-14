import os
from time import sleep
import tkinter as tk
import tkinter.ttk
import sys
import json
from Base import *
from main import run

PATH_PATH = 'path.json'

def redirect_std_to_text(out, err): 
    class StdoutRedirector(object): 
        def __init__(self, text_widget): 
            self.text_widget = text_widget 

        def write(self, message):
            self.text_widget.insert(tk.END, message) 
        
        def flush(self):
            pass

    sys.stdout = StdoutRedirector(out)
    sys.stderr = StdoutRedirector(err)

def init_path_json():
    if not os.path.exists(PATH_PATH):
        with open(PATH_PATH, 'w') as f:
            json.dump({'jar_path': 'xxx.jar', 'run_path': 'D:/xxx/', 'account':1}, f, indent=4, ensure_ascii=False)

    with open(PATH_PATH, 'r') as f:
        data = json.load(f)
    jar_name.insert(0, data['jar_path'])
    run_path.insert(0, data['run_path'])
    account.insert(0, data['account'])
    # jar_path.update()
    # run_path.update()

def check_path():
    err.configure(state=tk.NORMAL)
    err.delete('1.0', tk.END)
    print('正在检查路径有效性.......请稍后', file=sys.stderr)
    err.update()
    sleep(1)
    err.delete('1.0', tk.END)
    with open(PATH_PATH, 'r') as f:
        data = json.load(f)
    if not os.path.exists(data['jar_path']):
        print('jar名无效或还未定义，请在输入框内重新输入并点击更新', file=sys.stderr)
    else:
        print('jar名检测通过', file=sys.stderr)
    print('当前文件名:' + data['jar_path'], file=sys.stderr)
    if not os.path.exists(data['run_path']):
        print('run路径无效或还未定义，请在输入框内重新输入并点击更新', file=sys.stderr)
    else:
        print('run路径检测通过', file=sys.stderr)
    print('当前路径:' + data['run_path'], file=sys.stderr)
    print('注意！！jar文件应位于run路径中', file=sys.stderr)
    err.configure(state=tk.DISABLED)

def update_path(key, entry):
    with open('path.json', 'r') as f:
        p = json.load(f)
    with open('path.json', 'w') as f:
        p[key] = entry.get()
        json.dump(p, f, indent=4, ensure_ascii=False)
    check_path()


def start_run():
    out.configure(state=tk.NORMAL)
    err.configure(state=tk.NORMAL)
    out.delete('1.0', tk.END)
    err.delete('1.0', tk.END)
    try:
        cnt = int(account.get())
    except:
        if len(account.get()) != 0:
            account.delete('1.0', tk.END)
        err.delete('1.0', tk.END)
        print('请输入评测次数：(非零整数)', file=sys.stderr)
        err.update()
        return
    progressbarOne = tkinter.ttk.Progressbar(root, value=0, maximum=cnt)
    progressbarOne.grid(row=4, rowspan=1, column=0, columnspan=10)
    os.chdir(run_path.get())
    print(os.getcwd())
    
    if not os.path.exists(OUT_DIR):
        os.mkdir(OUT_DIR)
    for i in range(1, 1+cnt):
        # testMode = random.choice(TEST_MODE)
        out.delete('1.0', tk.END)
        print(f'开始第 {i} 次评测')
        out.update()
        run(MODE_RAND, JAR_PATH=jar_name.get())
        err.delete('1.0', '2.0')
        if not err.get("1.0", "end-1c").strip():
            print(f'第 {i} 次评测通过', file=sys.stderr)
            err.update()
        else:
            print(f'第 {i} 次评测未通过', file=sys.stderr)
            err.update()
            break
        progressbarOne['value'] = i
        root.update()
    out.configure(state=tk.DISABLED)
    err.configure(state=tk.DISABLED)


root = tk.Tk()
ziti = font=("Times",13,"bold")
out = tk.Text(root, height=5, width=60,font=ziti)
out.grid(row=0, rowspan=5, column=0, columnspan=9)
err = tk.Text(root, height=5,width=70, font=ziti)
err.grid(row=0, rowspan=5,column=10, columnspan=10) 
redirect_std_to_text(out, err)

tk.Text(root, height=20,width=60, font=ziti).grid(row=5, rowspan=10, column=0, columnspan=10)

tk.Label(root, text='jar文件名',width=10).grid(row=5, column=10)
jar_name = tk.Entry(root, width=55)
jar_name.grid(row=5, rowspan=1, column=11, columnspan=4)
tk.Button(root, width=20, text='更新jar文件名', 
          command=lambda:update_path('jar_path', jar_name)).grid(row=5, rowspan=1, column=16, columnspan=3)

tk.Label(root, text='工作目录',width=10).grid(row=6, column=10)
run_path = tk.Entry(root, width=55)
run_path.grid(row=6, rowspan=1, column=11, columnspan=4)
tk.Button(root, width=20, text='更新工作路径', 
          command=lambda:update_path('run_path', run_path)).grid(row=6, rowspan=1, column=16, columnspan=3)

tk.Label(root, text='评测次数',width=10).grid(row=7, column=10)
account = tk.Entry(root, width=8,textvariable=tk.StringVar().set('10'))
account.grid(row=7, rowspan=1, column=11, columnspan=1)
tk.Button(root, width=20,text='开始评测',command=lambda:start_run()).grid(row=7, rowspan=1, column=12, columnspan=1)

tk.Button(root, width=20,text='检查所有路径',command=lambda:check_path()).grid(row=7, rowspan=1, column=13, columnspan=1)
# tk.Button(root, width=20,text='等待开发',command=lambda:start_run()).grid(row=7, rowspan=1, column=14, columnspan=1)
root.eval('tk::PlaceWindow . center')


init_path_json()
check_path()
root.mainloop()