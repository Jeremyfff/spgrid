import datetime
import os
import subprocess
import time

import npyscreen
from helper.global_var import *
from contextlib import redirect_stdout
import io

import threading


class App(npyscreen.NPSApp):

    def __init__(self, version: str = "None"):
        super(App, self).__init__()
        self.version = version

        self.currentForm = None  # 记录当前编辑的表单
        self.ms_list = []  # 记录表单的控件
        self.ms_idx = -1  # 记录纯选择项的表单空间选择项

        self.strio = io.StringIO()  # 截取系统strio 内容
        self.strio_gui = None  # 存放strio的控件
        self.io_update_thread = IO_Update(self)  # 定时更新GUI的进程

        self.tasks = []  # 记录正在运行的subprocess 任务
        self.task_status = {}  # 记录正在运行任务状态的dict， 以任务名为键值
        self.task_progress = {}  # 记录正在运行任务进度的dict  以任务名为键值
        self.output = ""
        self.exit_task = None
        self.exit_kwargs = ()
        self.exit = False



    def main(self):
        self.io_update_thread.start()
        while not self.exit:
            with redirect_stdout(self.strio):  # update every loop

                idx = self.GenSelectForm(self.MainMenu)
                self.currentForm.DISPLAY()
                # '''==============================================================================================='''
                # '''==============================================================================================='''
                if idx == 0:
                    # start a new solver
                    # get data
                    data = self.GenEditForm(self.StartNewSolverForm)
                    # process data
                    cancel = data[3].value
                    if cancel:
                        continue
                    fn = data[0].value
                    fn = fn.replace(SCRIPT_DIR, "")
                    nohup = False if data[1].value[0] == 1 else True

                    # add new solver to ps
                    ps = PS()
                    ps.AddSolver(P(name=fn, working_dir=''), write_to_disk=True)

                    # run
                    if nohup:
                        ExecPy(fn, nohup=nohup)  # exec py with nohup
                    else:  # exit helper and run
                        self.exit_task = ExecPy
                        self.exit_kwargs = (fn, nohup)
                        self.exit = True
                # ======================================================================================================
                elif idx == 1:
                    solver,all_solvers = self.Handle_SelectSolver_Running()
                    if solver:
                        solver.kill()
                        all_solvers.WriteToDisk(update=True)


                # ======================================================================================================
                elif idx == 2:
                    # process data
                    solver = self.Handle_SelectSolver()
                    if solver:
                        self.Handle_ProcessDataForm(solver=solver)

                # ======================================================================================================
                elif idx == 3:
                    # Manage Solvers
                    solver = self.Handle_SelectSolver()
                    if solver:
                        self.Handle_ManageSolver(solver)

                elif idx == 4:
                    # clean memory
                    ms = self.GenEditForm(self.SelectProgramTypeForm)
                    clean = False if ms[1].value is None else True
                    cancel = False if ms[2].value is None else True
                    if clean:
                        target_idx = ms[0].value
                        for idx in target_idx:
                            pn = CLEAN_TARGETS[idx]
                            KillProgramByName(pn)

                elif idx == 5:
                    # view output
                    F = npyscreen.Form(name="action form", ALLOW_RESIZE=True, width=40, height=30)
                    self.strio_gui = F.add(npyscreen.TitlePager, values=self.get_strio())
                    F.edit()
                    continue
                else:
                    break

        out = self.get_strio()
        self.output = out
        self.exit = True

    def GenEditForm(self, Func, **kwargs):
        F = Func.__call__(**kwargs)
        self.currentForm = F

        F.edit()
        return self.ms_list

    def GenSelectForm(self, Func, **kwargs):
        self.ms_idx = -1
        F = Func.__call__(**kwargs)
        self.currentForm = F
        F.edit()
        return self.ms_idx

    def ExampleForm(self):
        F = npyscreen.Form(name="Welcome to Topo_opt_helper", )
        t = F.add(npyscreen.TitleText, name="Text:", )
        fn = F.add(npyscreen.TitleFilename, name="Filename:")
        fn2 = F.add(npyscreen.TitleFilenameCombo, name="Filename2:")
        dt = F.add(npyscreen.TitleDateCombo, name="Date:")
        s = F.add(npyscreen.TitleSlider, out_of=12, name="Slider")
        ml = F.add(npyscreen.MultiLineEdit,
                   value="""try typing here!\nMutiline text, press ^R to reformat.\n""",
                   max_height=5, rely=9)
        ms = F.add(npyscreen.TitleSelectOne, max_height=4, value=[1, ], name="Pick One",
                   values=["Option1", "Option2", "Option3"], scroll_exit=True)
        ms2 = F.add(npyscreen.TitleMultiSelect, max_height=-2, value=[1, ], name="Pick Several",
                    values=["Option1", "Option2", "Option3"], scroll_exit=True)
        return F

    def MainMenu(self):
        F = npyscreen.Form(name=f"Welcome, select a function version:{self.version}")
        items = ["1. Start a new solver", "2. Stop solver", "3. Process Data", "4. Manage Solvers", "5. Clean Memory",
                 "6. StdOut"]
        self.ms_list = []
        for i in items:
            ms = F.add(npyscreen.ButtonPress, max_height=6, name=i,
                       scroll_exit=True, when_pressed_function=self.exit_idx)
            self.ms_list.append(ms)
        self.strio_gui = F.add(npyscreen.TitlePager, name="std out", values=self.get_strio(), editable=False)
        F.DISPLAY()
        return F

    def SelectSolver(self, solvers=None):
        if solvers == None:
            solvers = PS().GetSolvers(reverse=True)  # update information
        F = npyscreen.Form(name="Please select a solver", )
        info = []
        count = 0
        for solver in solvers:
            info.append(f"{count} {solver.briefInfo(limit=50)}")
            count += 1
        self.ms_list = []
        for i in info:
            ms = F.add(npyscreen.ButtonPress, max_y=30, name=i,
                       scroll_exit=True, when_pressed_function=self.exit_idx)
            self.ms_list.append(ms)
        self.strio_gui = None
        return F

    def StartNewSolverForm(self):
        target_name = ListFiles(SCRIPT_DIR, reverse=True, end='.py', sort_type='mtime')[0]
        F = npyscreen.FormBaseNew(name="Start A New Solver")
        self.ms_list = []
        self.ms_list.append(F.add(npyscreen.TitleFilenameCombo, name="Filename:", value=target_name))
        self.ms_list.append(F.add(npyscreen.TitleSelectOne, max_height=2, value=[0, ], name="nohup?",
                                  values=["Yes", "No"], scroll_exit=True))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Run Solver",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Cancel",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.strio_gui = None
        return F

    def ProcessDataForm(self, solver):
        fns = ListFiles(os.path.join(solver.working_dir, "fem"), reverse=False, end=".tcb.zip", sort_type="name")
        plys = ListFiles(os.path.join(solver.working_dir, "fem"), reverse=False, end=".ply.zip", sort_type="name")
        fns = RemoveSuffixList(fns)
        plys = RemoveSuffixList(plys)

        diff_fns = []
        for fn in fns:
            find = False
            for ply in plys:
                if fn == ply:
                    find = True
                    break
            if not find:
                diff_fns.append(fn)

        fns = diff_fns
        fns_r = []
        for i in range(len(fns)):
            if i % 10 == 0:
                fns_r.append([str(fns[i])])
            else:
                fns_r[-1].append(" " + str(fns[i]))



        # 选择如何处理数据
        F = npyscreen.FormBaseNew(name="ProcessData")
        self.ms_list = []
        # F.add(npyscreen.TitlePager, name="[info]", values=["target folder:",AbbreviateContent(solver.working_dir,limit=40)], editable=False)
        F.add(npyscreen.FixedText, value=f"target folder:{AbbreviateContent(solver.working_dir, limit=40)}")
        self.ms_list.append(F.add(npyscreen.TitleSelectOne, max_height=4, value=[3, ], name="[Target]",
                                  values=[".tcb", ".txt", ".ply", ".ply.zip"], scroll_exit=True))
        self.ms_list.append(F.add(npyscreen.TitleSelectOne, max_height=3, value=[1, ], name="[Select File]",
                                  values=["All", "Last", "Custom idx"], scroll_exit=True))
        self.ms_list.append(F.add(npyscreen.TitleText, name="custom idx:"))
        self.ms_list.append(F.add(npyscreen.TitleSlider, out_of=8, name="[Threads]", value=4))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Process",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Process(nohup)",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Cancel",
                                  scroll_exit=True, when_pressed_function=self.exit_func))

        F.add(npyscreen.TitlePager, name="[raw files]", values=fns_r, editable=False)
        self.strio_gui = None
        F.DISPLAY()
        return F

    def ManageSolverForm(self, solver):
        fem_path = os.path.join(solver.working_dir, "fem")
        tcb_zips = ListFiles(fem_path, reverse=False, end=".tcb.zip", sort_type="name")
        tcbs = ListFiles(fem_path, reverse=False, end=".tcb", sort_type="name")
        txts = ListFiles(fem_path, reverse=False, end=".txt", sort_type="name")
        plys = ListFiles(fem_path, reverse=False, end=".ply", sort_type="name")
        header = f".tcb.zip: {len(tcb_zips)} .tcb: {len(tcbs)} .txt: {len(txts)} .ply {len(plys)}"

        showing_file_list =[]
        size_list = []
        gap = int(len(tcb_zips) / 15.0)
        if gap < 1:
            gap = 1
        for i in range(len(tcb_zips)):
            if i % gap != 0 and i != len(tcb_zips) - 1:
                continue
            fn = tcb_zips[i]
            showing_file_list.append(fn)

        for fn in showing_file_list:
            file_size = os.path.getsize(os.path.join(fem_path, fn)) / 1024
            size_list.append(file_size)
        sorted_file_size = sorted(size_list)
        min = sorted_file_size[0]
        max = sorted_file_size[-1]
        size_info = []
        for i in range(len(showing_file_list)):
            file_size = size_list[i]
            c = int(file_size / max * 50)
            line = f"{showing_file_list[i]}: |"
            for i in range(c):
                line += "#"
            for i in range(50-c):
                line += "-"
            line += f"| {round(file_size / 1024, 2)}MiB"
            size_info.append(line)
        size_info.reverse()
        # 选择如何处理数据
        F = npyscreen.FormBaseNew(name="Select a Function")
        self.ms_list = []
        F.add(npyscreen.FixedText, value=f"folder info:{header}")

        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Delete",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Process",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Cancel",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        F.add(npyscreen.TitlePager, name="[size viewer]", values=size_info, editable=False)

        self.strio_gui = None
        F.DISPLAY()
        return F

    def SelectProgramTypeForm(self):
        self.ms_list = []
        F = npyscreen.FormBaseNew(name="", )

        self.ms_list.append(F.add(npyscreen.TitleMultiSelect, max_height=3, value=[ ], name="Pick Several",
                    values=CLEAN_TARGETS, scroll_exit=F))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Clean",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Cancel",
                                  scroll_exit=True, when_pressed_function=self.exit_func))
        self.strio_gui = None
        F.DISPLAY()
        return F
    def YesNoForm(self):
        F = npyscreen.FormBaseNew(name="")
        self.ms_list = []
        F.add(npyscreen.FixedText, value=f"Confirm ?")
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="Yes",
                                  scroll_exit=True, when_pressed_function=self.exit_idx))
        self.ms_list.append(F.add(npyscreen.ButtonPress, name="No",
                                  scroll_exit=True, when_pressed_function=self.exit_idx))
        self.strio_gui = None
        F.DISPLAY()
        return F

    def exit_idx(self):
        self.ms_idx = -1
        for i in range(len(self.ms_list)):
            if self.ms_list[i].value:
                self.ms_idx = i
                break
        self.exit_func()

    def exit_func(self):
        self.currentForm.editing = False

    def get_strio(self, limit=-1, reverse=False):
        content = self.strio.getvalue().split("\n")
        clear = False
        if len(content) > 100:
            clear = True
        if limit == -1:
            if reverse:
                content.reverse()
                return content
            else:
                return content
        l = limit if len(content) > limit else len(content)
        content.reverse()
        content = content[0:l]
        if not reverse:
            content.reverse()

        if clear:
            self.clear_strio()

        return content

    def clear_strio(self):
        self.strio.close()
        self.strio = io.StringIO()

    def stop_all_tasks(self):
        for task in self.tasks:
            task.kill()
        self.tasks = []
        self.task_status = {}
        self.task_progress = {}


    def Handle_ProcessDataForm(self,solver):
        ms = self.GenEditForm(self.ProcessDataForm, solver=solver)
        fem_path = os.path.join(solver.working_dir, "fem")
        target = ms[0].value[0]
        file_mode = ms[1].value[0]
        custom_idx_str = ms[2].value
        thread_num = int(ms[3].value)
        next = False if ms[4].value is None else True
        nohup = False if ms[5].value is None else True
        cancle = False if ms[6].value is None else True
        # break condition
        if cancle or not next:
            print("user cancel")
            return

        # get files
        selected_files = []
        print(fem_path)
        all_files = ListFiles(fem_path, False, end=".tcb.zip", sort_type='name')
        if file_mode == 0:
            # all files
            selected_files = all_files
        elif file_mode == 1:
            # last file
            r_all_files = all_files.copy()
            r_all_files.reverse()
            f = r_all_files[0]
            selected_files = [f]
        elif file_mode == 2:
            if custom_idx_str == "":
                print("[error] plese type in custom idx")
                return
            try:
                for part in custom_idx_str.split(","):
                    if "-" in part:
                        parts = part.split("-")
                        if parts[0] == "start":
                            parts[0] = "0"
                        if parts[1] == "end":
                            parts[1] = str(len(all_files))
                        start = int(parts[0])
                        end = int(parts[1])
                        if end < start:
                            start, end = end, start
                        start = 0 if start < 0 else start
                        end = len(all_files) if end > len(all_files) else end
                        files_to_add = all_files[start:end]
                        for f in files_to_add:
                            selected_files.append(f)
                    else:
                        if part == "start":
                            part = "0"
                        if part == "end":
                            part = str(len(all_files))
                        idx = int(part)
                        selected_files.append(all_files[idx])
            except Exception as e:
                print(f"[error] {str(e)}")
                return
        assert len(selected_files) > 0

        # 根据thread分配文件
        selected_files_dict = {}
        for i in range(len(selected_files)):
            block = i % thread_num
            if block not in selected_files_dict.keys():
                selected_files_dict[block] = [selected_files[i]]
            else:
                selected_files_dict[block].append(selected_files[i])
        print(selected_files_dict)
        if not nohup:
            # 清空任务
            self.exit_task = []
            self.exit_kwargs = []
            self.stop_all_tasks()  # 停止所有任务
        for block in selected_files_dict:
            # 分区快其中任务
            file_in_block = selected_files_dict[block]  # 提取该block的文件
            # 生成file_list 参数内容
            fib_str = ""
            for f in file_in_block:
                fib_str += f + ","
            fib_str = fib_str[:-1]  # 去除最后的逗号
            kwargs = {'block': block, 'target': target, 'file_list': fib_str, 'fem_path': fem_path}
            if nohup:
                ExecPy(os.path.join(SCRIPT_DIR, 'utils/helper/exec_human_readable.py'), True, kwargs)
            else:
                task = ExecPy(os.path.join(SCRIPT_DIR, 'utils/helper/exec_human_readable.py'), False,
                              kwargs)
                self.tasks.append(task)  # 将任务加入任务列表
                taskMonitor = TaskMonitor(self, task, f"block{str(block)}")
                taskMonitor.start()

    def Handle_SelectSolver(self):
        solvers = PS().GetSolvers(reverse=True)
        idx2 = self.GenSelectForm(self.SelectSolver, solvers=solvers)
        if idx2 == -1:
            print("user cancel")
            return None
        solver = solvers[idx2]
        return solver

    def Handle_SelectSolver_Running(self):
        # stop solvers
        all_solvers = PS()
        running_solvers = all_solvers.GetRunningSolvers(reverse=True)
        idx2 = self.GenSelectForm(self.SelectSolver, solvers=running_solvers)
        if idx2 == -1:
            print("user cancel")
            return None,None
        else:
            solver = running_solvers[idx2]
            return solver, all_solvers

    def Handle_ManageSolver(self, solver):
        ms = self.GenEditForm(self.ManageSolverForm, solver=solver)
        delete = False if ms[0].value is None else True
        process = False if ms[1].value is None else True
        cancel = False if ms[2].value is None else True
        if cancel:
            print("user cancel")
            return
        if delete:
            idx3 = self.GenSelectForm(self.YesNoForm)
            print(f"idx3: {idx3}")
            if idx3 == 0:
                # yes
                ExecCmd(f"rm {solver.working_dir}")
                print(f"{solver.working_dir} removed!")

            else:
                self.Handle_ManageSolver(solver)
        elif process:
            self.Handle_ProcessDataForm(solver)


class IO_Update(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.counter = 0

    def is_any_task_running(self):
        if len(self.app.tasks) == 0:
            return False
        task_names = list(self.app.task_status.keys())
        task_status = list(self.app.task_status.values())

        for i in range(len(task_names)):
            if task_status[i] is None:
                return True
        return False

    def should_print_task_info(self):
        # 这个counter只有达到2时才会停止输出
        if self.is_any_task_running():
            self.counter = 0
            return True
        else:
            self.counter += 1
        if self.counter >= 2:
            return False
        return True

    def process_status_and_progress(self):
        # 根据自身的task status 生成对应的额信息
        if len(self.app.task_status) == 0:
            return "============================\n    no task running    \n============================"
        msg = "============================\n"
        task_names = list(self.app.task_status.keys())
        task_status = list(self.app.task_status.values())
        task_progress = list(self.app.task_progress.values())
        for i in range(len(task_status)):
            status = "working " if task_status[i] is None else "finished"
            try:
                progress = task_progress[i]
            except:
                progress = "N/A"
            msg += f"{task_names[i]}: {status} | {progress}\n"
        msg += "============================"
        return msg

    def run(self):
        while not self.app.exit:
            if self.app.strio_gui is not None:
                if self.should_print_task_info():
                    print(self.process_status_and_progress())
                    print(datetime.datetime.now().strftime("%D%M%S"))
                self.app.strio_gui.values = self.app.get_strio(reverse=True)
                self.app.strio_gui.display()
            time.sleep(1)


class TaskMonitor(threading.Thread):
    def __init__(self, app, task, name):
        # 每个任务伴随一个monitor
        threading.Thread.__init__(self)
        self.app = app
        self.task = task
        self.name = name

    def run(self):
        while not self.app.exit:
            status = self.task.poll()
            self.app.task_status[self.name] = status
            if status is None:
                # running
                line = str(self.task.stdout.readline().strip())[2:-1]
                if not line:
                    continue
                try:
                    parts = line.split(':')
                    if len(parts) > 1:
                        progress = parts[1][:-1]
                        self.app.task_progress[self.name] = progress
                        continue
                except Exception as e:
                    print(e)
                    continue
                print(f"task {self.name} out: {line}")
            else:
                # complete
                print(f"task {self.name} complete.")
                self.app.tasks.remove(self.task)
                self.app.task_status.pop(self.name)
                self.app.task_progress.pop(self.name)
                break


def ExecCmd(cmd: str, print_out: bool = False):
    """
    执行本地命令
    :param print_out: 是否打印输出
    :param cmd: 命令内容
    :return: 执行结果
    """
    r = os.popen(cmd)
    out = r.read()
    r.close()
    if print_out:
        print(out)
    return out


def OsSys(cmd: str):
    os.system(cmd)


def StrKwargs(kwargs):
    kwargs = dict(kwargs)
    sufix = ""
    for key in kwargs:
        value = kwargs[key]
        sufix += f" --{key} {value}"
    return sufix


def ExecPy(fn, nohup=True, kwargs=None):
    if kwargs is None:
        kwargs = {}
    file_path = os.path.join(SCRIPT_DIR, fn)
    if nohup:
        cmd = f"nohup python3 {file_path}{StrKwargs(kwargs)} &"
        print(f"Executing: {cmd}")
        os.system(cmd)
        return None
    else:
        cmd = f"python3 {file_path}{StrKwargs(kwargs)}"
        # out = subprocess.Popen(cmd,shell=True)
        cmd = cmd.split(" ")
        out = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return out


def KillProgram(PIDS):
    """
    根据PID结束进程
    :param PIDS:
    :return:
    """
    pid_self = str(os.getpid())
    for i in range(len(PIDS) - 1):
        Id = PIDS[i]
        if Id == pid_self:
            print("ignore self")
            continue
        os.system('kill -9 ' + Id)
        print(f"PID: {Id} Killed")


def KillProgramByName(name):

    programIsRunningCmd = "ps -ef|grep " + name + "|grep -v grep|awk '{print $2}'"
    programIsRunningCmdAns = ExecCmd(programIsRunningCmd)
    ansLine = programIsRunningCmdAns.split('\n')
    if len(ansLine) >= 2:
        print(f"{len(ansLine) - 1} running {name} found")
        KillProgram(ansLine)
    else:
        print(f"no running {name} found")
    return len(ansLine) - 1


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


def AbbreviateContent(text: str, limit=50):
    assert limit >= 10
    brief_str = f"{text[0:int(limit / 2) - 1]}...{text[-int(limit / 2) + 1:-1] + text[-1]}" if len(
        text) > limit else text
    return brief_str


class P:
    def __init__(self, name, working_dir="", killed=False):
        self.name = name
        self.working_dir = working_dir
        self.__killed__ = killed

    def isRunning(self):
        if self.__killed__:
            return False
        programIsRunningCmd = "ps -ef|grep " + self.name + "|grep -v grep|awk '{print $2}'"
        programIsRunningCmdAns = ExecCmd(programIsRunningCmd)
        ansLine = programIsRunningCmdAns.split('\n')
        return True if len(ansLine) >= 2 else False

    def __str__(self):
        running_status = "running" if self.isRunning() else "stopped"
        simplified_working_dir = self.working_dir.replace(OUTPUT_DIR, "%OUTPUT%/")
        return f"{self.name} | {running_status} | {simplified_working_dir}"

    def briefInfo(self, limit=50):
        brief_name = self.name.replace(".py", "").replace("opt_", "")
        running_status = "running" if self.isRunning() else "stopped"
        simplified_working_dir = self.working_dir.replace(OUTPUT_DIR, "").replace(brief_name + "/", "").replace("task-",
                                                                                                                "")
        brief_dir = AbbreviateContent(simplified_working_dir, limit)
        return f"{running_status} | {brief_name} | {brief_dir}"

    def kill(self):
        KillProgramByName(self.name)
        self.__killed__ = True


class PS:
    def __init__(self, file_path: str = "ps.txt"):
        self.file_path = file_path
        self.__solvers__ = []
        find_removed_solver = False
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()

            for line in lines:
                if line == "\n":
                    continue
                line = line.replace("\n", "").split(",")
                name = line[0]
                working_dir = ""
                if len(line) > 1:
                    working_dir = line[1]
                killed = False
                if len(line) > 2:
                    killed = True if line[2] == "killed" else False
                if name not in self.GetNames() or working_dir not in self.GetWorkingDirs():
                    if len(working_dir) > 0 and not os.path.exists(working_dir):
                        find_removed_solver = True
                        print(f"find removed solver: {name}")
                        continue
                    self.AddSolver(P(name, working_dir, killed), write_to_disk=False)
        if find_removed_solver:
            self.WriteToDisk(update=False)

    def __str__(self):
        count = 0
        s = ""
        for p in self.GetSolvers():
            s += f"{count} | {str(p)}\n"
            count += 1
        return s

    def __len__(self):
        return len(self.GetSolvers())

    def __getitem__(self, item):
        return self.__solvers__.__getitem__(item)

    def Update(self):
        self.__init__(self.file_path)

    def AddSolver(self, solver, write_to_disk=True):
        self.__solvers__.append(solver)
        if write_to_disk:
            self.WriteToDisk()

    def RemoveSover(self, solver, write_to_disk=True):
        self.__solvers__.remove(solver)
        if write_to_disk:
            self.WriteToDisk()

    def WriteToDisk(self, limit=10, update=True):
        l = limit if self.__solvers__.__len__() > limit else self.__solvers__.__len__()
        valid_solvers = self.__solvers__.copy()
        valid_solvers.reverse()
        valid_solvers = valid_solvers[0:l]
        valid_solvers.reverse()

        with open(self.file_path, "w", encoding='utf-8') as f:
            for solver in valid_solvers:
                line = "\n" + solver.name
                if solver.working_dir != "":
                    line += "," + solver.working_dir
                if solver.__killed__:
                    line += ",killed"
                f.write(line)
            f.close()
        if update:
            self.Update()

    def GetNames(self):
        names = []
        for p in self.__solvers__:
            names.append(p.name)
        return names

    def GetWorkingDirs(self):
        dirs = []
        for p in self.__solvers__:
            dirs.append(p.working_dir)
        return dirs

    def GetSolvers(self, reverse=False):
        results = self.__solvers__.copy()
        if reverse:
            results.reverse()
        return results

    def GetRunningSolvers(self, reverse=False):
        result = []
        for solver in self.__solvers__:
            if solver.isRunning():
                result.append(solver)
        if reverse:
            result.reverse()
        return result

    def GetLatest(self):
        return self.__solvers__[-1]
