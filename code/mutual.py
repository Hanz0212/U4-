from func import *
from Base import *
import difflib
from filediff.diff import file_diff_compare

def check_mutual(pn) :
    for i in range(len(pn) - 1) :
        if not check_mutual2(pn[i], pn[i + 1]) :
            return False
    return True

def check_mutual2(p1, p2) :
    with open(p1 + '.out', "r") as f1:
        with open(p2 + '.out', "r") as f2:
            text1 = f1.readlines()
            text2 = f2.readlines()
    file_diff_compare(p1 + '.out', p2 + '.out', diff_out='dif.html', show_all=True, no_browser=True)
    ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
    if (ratio != 1):
        print("diffrent between " + p1 + ' ' + p2)
        file_diff_compare(p1 + '.out', p2 + '.out', diff_out='simpleDiff.html', show_all=False, no_browser=False)
        file_diff_compare(p1 + '.out', p2 + '.out', diff_out='allDiff.html', show_all=True, no_browser=False)
        return False
    return True

if __name__ == '__main__':
    os.chdir(RUN_PATH)
    merge_file(IN_PATH, APP_PATH, MER_PATH) # 将初始输入和根据输出新增的输入合并到新文件
    pn = get_jar_names()
    for file in pn:
        cmd = ["java", "-jar", file + '.jar', "<", MER_PATH, ">", RUN_PATH + MUTUAL_OUT_DIR + file + '.out']
        os.system(" ".join(cmd))
    os.chdir(MUTUAL_OUT_DIR)
    check_mutual(pn)