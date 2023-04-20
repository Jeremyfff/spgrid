import configparser
import datetime
import os
import threading
import time

config = configparser.ConfigParser()

target_name = ""
folder_path = "/hy-tmp/taichi/projects/spgrid/scripts/"
threshold = 0


def ExecCmd(cmd):
    """
    执行命令
    :param cmd: 命令内容
    :return: 执行结果
    """
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text


def Kill_program(PIDS):
    """
    根据PID结束进程
    :param PIDS:
    :return:
    """
    for i in range(len(PIDS) - 1):
        Id = PIDS[i]
        os.system('kill -9 ' + Id)
        print(f"PID: {Id} Killed")


def Kill_program_byName(name):
    programIsRunningCmd = "ps -ef|grep " + name + "|grep -v grep|awk '{print $2}'"
    programIsRunningCmdAns = ExecCmd(programIsRunningCmd)
    ansLine = programIsRunningCmdAns.split('\n')
    if len(ansLine) >= 2:
        print(f"{len(ansLine) - 1} running {name} found")
        Kill_program(ansLine)
    else:
        print(f"no running {name} found")
    return len(ansLine) - 1


def Get_ps():
    ps = {}
    with open("ps.txt", "r", encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            if line == "\n":
                continue
            line = line.replace("\n", "").split(",")
            name = line[0]
            if len(line) > 1:
                dir = line[1]
            else:
                dir = ""
            if name not in ps.keys():
                ps[name] = dir
    return ps


def Detect_running_solver(ps):
    count = 0
    for name in ps.keys():
        programIsRunningCmd = "ps -ef|grep " + name + "|grep -v grep|awk '{print $2}'"
        programIsRunningCmdAns = ExecCmd(programIsRunningCmd)
        ansLine = programIsRunningCmdAns.split('\n')
        if len(ansLine) >= 2:
            count += 1
    return count


def Read_config():
    global folder_path
    global target_name
    global config
    config.read("config.ini")
    folder_path = config.get('basic', 'folder_path')
    target_name = config.get('basic', 'target_name')


def ExecPy(file_name, nohup=True):
    global folder_path
    file_path = os.path.join(folder_path, file_name)
    with open("ps.txt", 'w', encoding='utf-8') as f:
        f.write(file_name)
        f.close()

    if nohup:
        cmd = f"nohup python3 {file_path} &"
    else:
        cmd = f"python3 {file_path}"
    print(cmd)
    os.system(cmd)


def Get_all_files(path, end=""):
    for root, ds, fs in os.walk(path):
        for f in fs:
            if end != "":
                if f.endswith(end):
                    yield f
            else:
                yield f


def File_list_from_ps(ps,end=".tcb.zip"):
    dirs = []
    for dir in ps.values():
        dirs.append(dir)
    dir = os.path.join(dirs[0], "fem")
    print(f"searching in {dir}")
    file_list = get_file_list(dir, reverse=False, end=end)
    return file_list, dir


def Select_files_in_file_list(file_list):
    index_range = []
    retry_count = 3
    for i in range(retry_count):
        try:
            index = input("selct which one?[all,last,number]")
            if index == "all":
                index_range = range(len(file_list))
                break
            elif index == "last":
                index_range = [len(file_list) - 1]
                break
            elif index.__contains__("-"):
                tmp = index.split("-")
                a = int(tmp[0])
                b = int(tmp[1])
                if a > b:
                    a, b = b, a
                if a < 0:
                    a = 0
                if b > len(file_list):
                    b = len(file_list)
                index_range = range(a, b)
                break
            else:
                a = int(index)
                if a < 0 or a >= len(file_list):
                    raise Exception("invalid index")
                index_range = [int(index)]
                break
        except Exception as e:
            print(e)
            print("please retry")
    selected_files = []
    for index in index_range:
        selected_files.append(file_list[index])
    return selected_files


def get_resolution(lines):
    for line in lines:
        if line.startswith("    resolution: "):
            tmp = line.split("[")[1]
            tmp = tmp.split("]")[0]
            di = tmp.split(",")
            di_x = (int)(di[0].strip())
            di_y = (int)(di[1].strip())
            di_z = (int)(di[2].strip())
            return di_x, di_y, di_z
    return 0, 0, 0


# 从方括号的文本中获取xyz值
def value_from_square_brackets(square_brackets):
    tmp = square_brackets.strip()[1:-1].split(",")
    x = int(tmp[0].strip())
    y = int(tmp[1].strip())
    z = int(tmp[2].strip())
    return x, y, z


# 从base_coordinates_line文本中获取base_coordinate
def get_base_coordinate(base_coordinates_line):
    square_brackets = base_coordinates_line.split(":")[1]
    x, y, z = value_from_square_brackets(square_brackets)
    base = (x, y, z)
    return base


def get_coord_value(line, base):
    tmp = line.split(":")
    _x, _y, _z = value_from_square_brackets(tmp[0])
    value = float(tmp[1].strip())
    coord = (_x + base[0], _y + base[1], _z + base[2])
    return coord, value


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
    exec_time = time.time() - start_time

    # print(f"complete | total vertivces {vertices} | time {exec_time} sec")

def count_blocks(lines):
    block = 0
    for i in range(len(lines)):
        if lines[i] == "      [" + str(block) + "]: {\n":
            block += 1
    return block

def count_valid_points(lines, threshold):
    block = 0
    vertices = 0
    # print("counting valid points")
    for i in range(len(lines)):
        if lines[i] == "      [" + str(block) + "]: {\n":
            base = get_base_coordinate(lines[i + 1])
            # print(f"base: {base}")
            for j in range(64):
                coord, value = get_coord_value(lines[i + j + 2], base)
                if value > threshold:
                    vertices += 1
            block += 1
            continue
    return vertices
def count_valid_points_fast(lines):
    block = 0
    for i in range(len(lines)):
        if lines[i] == "      [" + str(block) + "]: {\n":
            block += 1
            continue
    return block * 64

class ConvertingThread(threading.Thread):
    def __init__(self, file_names, thread_idx):
        threading.Thread.__init__(self)
        self.file_names = file_names
        self.thread_idx = thread_idx

    def run(self):
        global workingThread
        global target_step
        global fem_dir
        global thread_info
        global threshold
        global remove_txt
        workingThread += 1
        print(f"running | {self.thread_idx}")

        if target_step >= 1:
            # 第一步
            thread_info[self.thread_idx]["step"] = 1  # update info
            for i in range(len(self.file_names)):
                thread_info[self.thread_idx]["file"] = i+1  # update info
                file = os.path.join(fem_dir, self.file_names[i])
                # print(f"[{self.thread_idx}] unzipping {file}")
                ExecCmd(f"unzip -d {fem_dir} -o {file}")

        if target_step >= 2:
            # 第二步
            thread_info[self.thread_idx]["step"] = 2  # update info
            # print(f"[{self.thread_idx}] converting to human readable txt...")
            for i in range(len(self.file_names)):
                thread_info[self.thread_idx]["file"] = i+1  # update info
                file = self.file_names[i].replace(".zip", "")  # 000000.tcb
                # print(f"[{self.thread_idx}] processing {file}")
                os.makedirs(f"{folder_path}tmp/{self.thread_idx}/", exist_ok=True)
                ExecCmd(
                    f"cd {folder_path}tmp/{self.thread_idx}/ && ti run convert_fem_solve {os.path.join(fem_dir, file)} --with-density")
                org_path = f"{folder_path}tmp/{self.thread_idx}/human_readable.txt"
                new_path = os.path.join(fem_dir, f"{file.replace('.tcb', '')}.txt")  # 000000.txt
                ExecCmd(f"mv {org_path} {new_path}")
                ExecCmd(f"rm {os.path.join(fem_dir, file)}")

        if target_step >= 3:
            thread_info[self.thread_idx]["step"] = 3  # update info
            for i in range(len(self.file_names)):
                thread_info[self.thread_idx]["file"] = i+1  # update info
                file = self.file_names[i].replace(".tcb.zip", ".txt")
                input_path = os.path.join(fem_dir, file)
                # print(f"[{self.thread_idx}] converting .ply from {file}")
                thread_info[self.thread_idx]["progress"] = 0.0  # update info
                with open(input_path, 'r') as f:
                    lines = f.readlines()
                thread_info[self.thread_idx]["progress"] = 0.2  # update info
                if threshold != 0:
                    valid_points = count_valid_points(lines, threshold)
                else:
                    valid_points = count_valid_points_fast(lines)
                thread_info[self.thread_idx]["progress"] = 0.5  # update info
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
                output_path = os.path.join(fem_dir, file.replace(".txt", ".ply"))
                exec_blocks(lines, prefix, output_path, threshold=threshold)
                if remove_txt:
                    ExecCmd(f"rm {input_path}")
                thread_info[self.thread_idx]["progress"] = 1.0  # update info


        workingThread -= 1



def get_file_list(file_path, reverse = False, end=".py"):
    """
    :param file_path: the file path where you want to get file
    :return: list, files sorted by name
    """
    dir_list = os.listdir(file_path)
    if not dir_list:
        return
    py_list = []
    for x in dir_list:
        if x.endswith(end):
            py_list.append(x)
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        py_list = sorted(py_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)),reverse=reverse)
        # dir_list = sorted(dir_list, key=lambda x: int(x[:-4]))  # 按名称排序
        # print(dir_list)
        return py_list







if __name__ == "__main__":
    dir_list = get_file_list(folder_path)
    print(dir_list)
    # os.system("source /opt/intel/intel2019u5.sh")


    while True:
        print("===============================")
        Read_config()
        ps = Get_ps()
        running = Detect_running_solver(ps)

        helper_msg = '''
1. Start a new solver   2. Stop solver
3. Process Data         4. View Progress
5. Exit
[user]: '''
        if running:
            print(f"[Info]: Solver running | {ps}")
            choice = input(helper_msg)
            if choice == "1":
                print("[Warning]: Cannot start a new solver")
                continue
        else:
            print("[Info]: No solver running")
            choice = input(helper_msg)

        if choice == "1":
            try:
                target_name = get_file_list(folder_path, reverse=True,end='.py')[0]
            except Exception as e:
                print(f"[error] no file found in {folder_path}")
            n = input(f"file_name ([{target_name}] by default):")
            if n != "":
                full_path = os.path.join(folder_path, n)
                print(full_path)
                if os.path.exists(full_path):
                    target_name = n
                    # config.set('basic', 'target_name', target_name)
                    # print("config updated")
                else:
                    print("[Error]: file not exist")
                    continue
            with open(os.path.join(folder_path, target_name), "r", encoding="utf-8") as f:
                line_count = 1
                find_error = False
                for line in f.readlines():
                    if "projects/topo_opt/data/" in line:
                        print(f"[warning] path not exist.\nline[{line_count}]: {line}")
                        input("back to menu? ")
                        find_error = True
                        break
                    line_count += 1
                if find_error:
                    continue
            #projects / topo_opt / data /
            n = input("nohup?[y/n]")
            if n == "y" or n == "":
                nohup = True
            else:
                nohup = False
            ExecPy(target_name, nohup=nohup)
            print(f"[Info]: starting solver [{target_name}] ", end="")
            while True:
                ps = Get_ps()
                if ps[target_name] != "":
                    print("\n")
                    break
                print(".", end="")
                time.sleep(0.5)
        elif choice == "2":
            for p in ps.keys():
                Kill_program_byName(p)
            if input("deep clean? (warning: this will close helper_working.py)[y/n]") == "y":
                Kill_program_byName("ti")
                Kill_program_byName("vim")
                # Kill_program_byName("sftp-server")
                Kill_program_byName("python3")
        elif choice == "3":
            # 检索文件夹
            if len(ps.values()) == 0:
                print("[Info]: No data history")
                continue
            file_list, fem_dir = File_list_from_ps(ps,end='.tcb.zip')
            print(f"find {len(file_list)} files\n{file_list}")

            # 确认处理目标
            c = input("Convert Target: 1.tcb 2.txt 3.ply")
            if c != "1" and c != "2" and c != "3":
                print("invalid input")
                continue
            target_step = int(c)


            # 是否要移除txt文件
            remove_txt = False
            if target_step == 3:
                c = input("remove txt?[y/n]")
                if c == "y" or c == "":
                    remove_txt = True

            # 选择要处理的文件
            selected_files = Select_files_in_file_list(file_list)
            if len(selected_files) == 0:
                print("no file selected")
                continue
            print(selected_files)

            # 处理的线程数
            thread_count = 4
            c = input("thread count:[4 by default]:")
            try:
                if c == "":
                    pass
                else:
                    thread_count = int(c)
            except Exception as e:
                print(e)

            # 开始处理
            workingThread = 0

            c = input(f"(thread = {thread_count}) proceed?[y/n]: ")
            if c == "y" or c == "":
                # 根据thread分配文件
                selected_files_dict = {}
                for i in range(len(selected_files)):
                    block = i%thread_count
                    if block not in selected_files_dict.keys():
                        selected_files_dict[block] = [selected_files[i]]
                    else:
                        selected_files_dict[block].append(selected_files[i])

                # 创建线程
                start_time = time.time()
                threads = []
                ii = 0
                for file_blocks in selected_files_dict.values():
                    thread = ConvertingThread(file_blocks, ii)
                    threads.append(thread)
                    ii += 1

                thread_info = []
                for i in range(len(threads)):
                    thread_info.append({"step":0, "total_step":target_step,"file":0,"total_file": len(selected_files_dict[i]), "progress":0.0})

                # 启动线程
                for thread in threads:
                    thread.start()
                    time.sleep(0.1)

                # 等待所有线程结束工作
                while workingThread > 0:
                    print("==================================================")
                    print(f"working threads: {workingThread} | working time:{time.time() - start_time} sec")
                    print("--------------------------------------------------")
                    for i in range(len(threads)):
                        c_step = thread_info[i]["step"]
                        t_step = thread_info[i]["total_step"]
                        c_file = thread_info[i]["file"]
                        t_file = thread_info[i]["total_file"]
                        c_progress = thread_info[i]["progress"]
                        if c_step == t_step and c_file == t_file and c_progress == 1.0:
                            print(f"thread {i} | Done")
                        else:
                            print(f"thread {i} | step:{c_step}/{t_step} | file:{c_file}/{t_file} | progress:{c_progress}/1.0")
                    time.sleep(1)
                print("==================================================")
                print(f"Done in {time.time() - start_time} sec")
            else:
                continue

        elif choice == "4":
            # 检索文件夹
            if len(ps.values()) == 0:
                print("[Info]: No running data or data history")
                continue
            file_list, fem_dir = File_list_from_ps(ps)
            print(f"iterations: {len(file_list)}")
            size_list = []
            for file in file_list:
                file_size = os.path.getsize(os.path.join(fem_dir, file)) / 1024
                size_list.append(file_size)
            sorted_file_size = sorted(size_list)
            min = sorted_file_size[0]
            max = sorted_file_size[-1]
            for i in range(len(size_list)):
                file_size = size_list[i]
                file_name = file_list[i]
                c = int(file_size / max * 50)
                info = f"{file_name}: "
                for i in range(c):
                    info += "#"
                info += f" {round(file_size/1024,3)}MiB"
                print(info)

        elif choice == "5":
            break

        time.sleep(1)