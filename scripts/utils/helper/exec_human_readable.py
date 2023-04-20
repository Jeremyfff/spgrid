import argparse
import random
import sys
import os
import time

FOLDER_PATH = "/hy-tmp/taichi/projects/spgrid/scripts/"


def ExecCmd(cmd: str, print_out: bool = False):

    r = os.popen(cmd)
    out = r.read()
    r.close()
    if print_out:
        print(out)
    return out


def OsSys(cmd: str):
    os.system(cmd)

# 从base_coordinates_line文本中获取base_coordinate
def get_base_coordinate(base_coordinates_line):
    square_brackets = base_coordinates_line.split(":")[1]
    x, y, z = value_from_square_brackets(square_brackets)
    base = (x, y, z)
    return base

# 从方括号的文本中获取xyz值
def value_from_square_brackets(square_brackets):
    tmp = square_brackets.strip()[1:-1].split(",")
    x = int(tmp[0].strip())
    y = int(tmp[1].strip())
    z = int(tmp[2].strip())
    return x, y, z

def get_coord_value(line, base):
    tmp = line.split(":")
    _x, _y, _z = value_from_square_brackets(tmp[0])
    value = float(tmp[1].strip())
    coord = (_x + base[0], _y + base[1], _z + base[2])
    return coord, value

def count_valid_points_fast(lines):
    block = 0
    for i in range(len(lines)):
        if lines[i] == "      [" + str(block) + "]: {\n":
            block += 1
            continue
    return block * 64

def count_valid_points_fast2(ff):
    block = 0
    while True:
        line = ff.readline()
        if line == "      [" + str(block) + "]: {\n":
            block += 1
            continue
        elif line == "":
            break
    return block * 64


def exec_blocks(lines, prefix, file_path, threshold = 0.0):
    start_time = time.time()
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prefix)
        f.close()
    with open(file_path, 'a', encoding='utf-8') as f:
        block = 0
        vertices = 0
        for i in range(len(lines)):
            if lines[i] == "      [" + str(block) + "]: {\n":
                # print(f"find block {block} : ")

                # 解析base coordinate
                base = get_base_coordinate(lines[i + 1])
                # print(f"base: {base}")
                for j in range(64):
                    coord, value = get_coord_value(lines[i + j + 2], base)
                    if value > threshold:
                        vertices += 1
                        # print(f"coord: {coord}  value: {value}")
                        f.write(f"{coord[0]} {coord[1]} {coord[2]} {value}\n")

                # print(f"block  {block} end")
                block += 1
                continue
        f.close()
    exec_time = time.time() - start_time

def exec_blocks2(f, prefix, file_path, threshold = 0.0):
    start_time = time.time()
    with open(file_path, 'w', encoding='utf-8') as ff:
        ff.write(prefix)
        ff.close()
    with open(file_path, 'a', encoding='utf-8') as ff:
        block = 0
        vertices = 0
        while True:
            line = f.readline()

            if line == "      [" + str(block) + "]: {\n":
                # print(f"find block {block} : ")

                # 解析base coordinate
                base = get_base_coordinate(f.readline())
                # print(f"base: {base}")
                for j in range(64):
                    coord, value = get_coord_value(f.readline(), base)
                    if value > threshold:
                        vertices += 1
                        # print(f"coord: {coord}  value: {value}")
                        ff.write(f"{coord[0]} {coord[1]} {coord[2]} {value}\n")

                # print(f"block  {block} end")
                block += 1
                continue
            elif line == "":
                break
            else:
                continue
        ff.close()
    exec_time = time.time() - start_time

def report_progress(idx:int, step:int, add_msg:str = ""):
    add_msg = add_msg + " | " if len(add_msg)>0 else ""
    step_msg = ""
    if step == 0:
        step_msg = "unzipping file"
    elif step == 1:
        step_msg = "convert to txt"
    elif step == 2:
        step_msg = "convert to ply"
    elif step == 3:
        step_msg = "zipping ply   "
    else:
        step_msg = "unknown step  "
    print(f"progress:processing {file_list[idx]} | {add_msg}current task {step_msg} | {len(file_list) - idx - 1} files left... ")
    sys.stdout.flush()
def ListFiles(file_path: str, reverse: bool = False, end: str = "", sort_type: str = "name"):
    """
    列出某个目录下的所有文件(原名：get_file_list)
    :param sort_type:
    :param reverse:
    :param end:
    :param file_path: the file path where you want to get file
    :return: list, files sorted by name
    """
    dir_list = os.listdir(file_path)
    # error checking
    if not dir_list:
        return
    # filter suffix
    if end != "":
        file_list = []
        for x in dir_list:
            if x.endswith(end):
                file_list.append(x)
    else:
        file_list = dir_list.copy()

    if sort_type == "mtime":
        file_list = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)), reverse=reverse)
    elif sort_type == "name":
        file_list.sort(reverse=reverse)
    elif sort_type == "ctime":
        file_list = sorted(file_list, key=lambda x: os.path.getctime(os.path.join(file_path, x)), reverse=reverse)

    return file_list

def RemoveSuffix(fn: str):
    """
    去除文件后缀
    :param fn:
    :return:
    """
    if "." in fn:
        fn = fn.split(".")[0]
    return fn


def RemoveSuffixList(fn_list: list):
    """
    给定一个列表，去除所有的后缀
    :param fn_list:
    :return:
    """
    new_fn_list = []
    if fn_list is None or len(fn_list) == 0:
        return new_fn_list
    for fn in fn_list:
        new_fn_list.append(RemoveSuffix(fn))
    return new_fn_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", type=int, default=0, help='block')
    parser.add_argument("--target", type=int, default=2, help='0. tcb  1. txt  2. ply')
    parser.add_argument("--file_list", type=str, default=" ", help='file in str, comma split')
    parser.add_argument("--fem_path", type=str, default=" ", help='fem path')

    args = parser.parse_args()

    # #sys.stdout.write(f"block: {args.block}  target: {args.target}  file_list: {args.file_list} fem_path: {args.fem_path}")
    # sys.stdout.flush()
    # start_time = time.time()
    # total_step = random.randint(10,100)
    # for i in range(total_step):
    #     print(f"progress:{i}/{total_step-1}")
    #     #sys.stdout.write(f"{args.block}-{i}")
    #     sys.stdout.flush()
    #     time.sleep(0.2)
    # print(f"progress:time {round(time.time() - start_time,1)}sec")
    # print(f"block {args.block} Done.")

    block = int(args.block)
    target = int(args.target)
    file_list = args.file_list.split(",")
    fem_path = args.fem_path

    start_time = time.time()

    tcb_zips = RemoveSuffixList(ListFiles(fem_path, reverse=False, end=".tcb.zip", sort_type="name"))
    tcbs = RemoveSuffixList(ListFiles(fem_path, reverse=False, end=".tcb", sort_type="name"))
    txts = RemoveSuffixList(ListFiles(fem_path, reverse=False, end=".txt", sort_type="name"))
    plys = RemoveSuffixList(ListFiles(fem_path, reverse=False, end=".ply", sort_type="name"))
    ply_zips = RemoveSuffixList(ListFiles(fem_path, reverse=False, end=".ply.zip", sort_type="name"))



    for i in range(len(file_list)):
        current_step = -2  # -2 代表没有这个tcb.zip文件，还没有算出来， -1代表还未执行任何操作 0表示已经完成了第0步，即解压，以此类推
        raw_name = file_list[i].replace(".tcb.zip","")
        for n in tcb_zips:
            if raw_name == n:
                current_step = -1
                break
        for n in tcbs:
            if raw_name == n:
                current_step = 0
                break
        for n in txts:
            if raw_name == n:
                current_step = 1
                break
        for n in plys:
            if raw_name == n:
                current_step = 2
                break
        for n in ply_zips:
            if raw_name == n:
                current_step = 3
                break
        # 最终取current_step的最高值

        print(f"current step: {current_step}")
        time.sleep(2)

        if target >= 0 and current_step < 0:
            # 第一步

            report_progress(i,0)  # 报告进度
            fn = file_list[i]  # .tcb.zip
            file = os.path.join(fem_path,fn)
            ExecCmd(f"cd {fem_path} && unzip -d {fem_path} -o {file}")  # 解压文件

        if target >= 1 and current_step < 1:
            # 第二步

            report_progress(i,1)  # 报告进度
            fn = file_list[i].replace(".zip", "")  # 000000.tcb

            os.makedirs(f"{FOLDER_PATH}tmp/{block}/", exist_ok=True)  # 创建临时文件夹
            out = ExecCmd(
                f"cd {FOLDER_PATH}tmp/{block}/ && ti run convert_fem_solve {os.path.join(fem_path, fn)} --with-density",print_out=True)
            # print(out)
            if out.__contains__("Permission"):
                print("error")
                break

            org_path = f"{FOLDER_PATH}tmp/{block}/human_readable.txt"
            new_path = os.path.join(fem_path, f"{fn.replace('.tcb', '.txt')}")  # 000000.txt
            ExecCmd(f"mv {org_path} {new_path}")
            ExecCmd(f"rm {os.path.join(fem_path, fn)}")


        if target >= 2 and current_step < 2:
            report_progress(i,2)
            fn = file_list[i].replace(".tcb.zip", ".txt")  # 00000.txt
            input_path = os.path.join(fem_path, fn)
            with open(input_path, 'r') as f:
                # lines = f.readlines()
                valid_points = count_valid_points_fast2(f)
                f.close()
                print(valid_points)
            with open(input_path, 'r') as f:
                prefix = f"ply\n" \
                         f"format ascii 1.0\n" \
                         f"comment author: Jeremy\n" \
                         f"comment object: Topo\n" \
                         f"element vertex {valid_points}\n" \
                         f"property float x\n" \
                         f"property float y\n" \
                         f"property float z\n" \
                         f"property float density\n" \
                         f"end_header\n"
                output_path = os.path.join(fem_path, fn.replace(".txt", ".ply"))
                exec_blocks2(f, prefix, output_path, threshold=0)
                ExecCmd(f"rm {input_path}")
                f.close()

        if target >= 3 and current_step < 3:
            report_progress(i,3)
            fn = file_list[i].replace(".tcb.zip", ".ply")  # 00000.ply
            output_name = fn.replace(".ply",".ply.zip")
            cmd = f"cd {fem_path} && zip {os.path.join(fem_path,output_name)} {os.path.join(fem_path,fn)}"
            # print(cmd)
            ExecCmd(cmd)
            ExecCmd(f"rm {os.path.join(fem_path,fn)}")

    print(f"progress:time {round(time.time() - start_time, 1)}sec")
    sys.stdout.flush()