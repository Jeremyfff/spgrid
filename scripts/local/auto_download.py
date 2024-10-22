"""
通过paramiko从远处服务器下载文件资源到本地
author: gxcuizy
time: 2018-08-01
"""
import sys
import time

import paramiko
import os
from stat import S_ISDIR as isdir

last_transferred = 0
last_time = 0
speed = 0
def progress_bar(transferred, toBeTransferred, suffix=''):
    global last_transferred
    global speed
    global last_time
    bar_len = 100
    filled_len = int(round(bar_len * transferred / float(toBeTransferred)))
    percents = round(100.0 * transferred / float(toBeTransferred), 1)
    bar = "\r["
    for i in range(filled_len):
        bar += "="
    for i in range(bar_len - filled_len):
        bar += " "
    bar += f"] {percents}%"

    time_ms = int(round(time.time() * 1000))
    time_gap = time_ms - last_time
    if time_gap > 0:
        speed = transferred - last_transferred
        speed /= float(time_gap)
        speed *= 1000
        speed /= 1024
        last_transferred = transferred
        last_time = time_ms

    bar += f"  {round(speed,2)} kb/s"
    print(bar,end="")


def down_from_remote(sftp_obj, remote_dir_name, local_dir_name, callback=None):
    global last_transferred
    global last_time
    """远程下载文件"""
    remote_file = sftp_obj.stat(remote_dir_name)
    if isdir(remote_file.st_mode):
        # 文件夹，不能直接下载，需要继续循环
        check_local_dir(local_dir_name)
        print('开始下载文件夹：' + remote_dir_name)
        for remote_file_name in sftp_obj.listdir(remote_dir_name):
            sub_remote = os.path.join(remote_dir_name, remote_file_name)
            sub_remote = sub_remote.replace('\\', '/')
            sub_local = os.path.join(local_dir_name, remote_file_name)
            sub_local = sub_local.replace('\\', '/')
            down_from_remote(sftp_obj, sub_remote, sub_local)
    else:
        # 文件，直接下载
        print('开始下载文件：' + remote_dir_name)
        last_transferred = 0
        last_time = int(round(time.time() * 1000))
        if callback is not None:
            sftp_obj.get(remote_dir_name, local_dir_name, callback=callback)
        else:
            sftp_obj.get(remote_dir_name, local_dir_name,callback=progress_bar)
        print("\n")
def upload_to_remote(sftp_obj,local_dir_name, remote_dir_name):
    """远程上传文件"""
    print('开始上传文件：' + remote_dir_name)
    sftp_obj.put(local_dir_name, remote_dir_name)


def check_local_dir(local_dir_name):
    """本地文件夹是否存在，不存在则创建"""
    if not os.path.exists(local_dir_name):
        os.makedirs(local_dir_name)


def exec_cmd(client, cmd):
    # 执行命令获得结果
    (stdin, stdout, stderr) = client.exec_command(cmd)

    output = stdout.readlines()
    error = stderr.readlines()
    if len(error) > 0:
        for line in error:
            print(line)
    return output


def Get_ps(path="./ps.txt"):
    names = []
    dirs = []
    with open(path, "r", encoding='utf-8') as f:
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
                continue
            names.append(name)
            dirs.append(dir)
    return names, dirs


def Get_remote_task_path(ps_path="./ps.txt"):
    names, dirs = Get_ps(ps_path)
    pths = []
    for v in dirs:
        pths.append(v)
    remote_task_path = pths[0]
    return remote_task_path

def Get_remote_task_path_list(ps_path="./ps.txt"):
    names, dirs = Get_ps(ps_path)
    return dirs

def Get_remote_task_name_list(ps_path ="./ps.txt"):
    names, dirs = Get_ps(ps_path)
    return names

def Get_shared_path(ps_path="./ps.txt"):
    remote_task_path = Get_remote_task_path(ps_path)
    _shared_path = remote_task_path.split("/")
    shared_path = _shared_path[-2] + "/" + _shared_path[-1] + "/"
    # print(f"shared_path: {shared_path}")
    return shared_path

def Get_shared_path_byselect(remote_task_path:str):
    _shared_path = remote_task_path.split("/")
    shared_path = _shared_path[-2] + "/" + _shared_path[-1] + "/"
    return shared_path

def get_file_list(file_path, reverse=False, end=".py"):
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
        py_list = sorted(py_list, key=lambda x: os.path.getmtime(os.path.join(file_path, x)), reverse=reverse)
        # dir_list = sorted(dir_list, key=lambda x: int(x[:-4]))  # 按名称排序
        # print(dir_list)
        return py_list


def get_remote_file_list(client, path, end=""):
    print("getting remote file list...")
    _remote_files = exec_cmd(client, f"cd {path} && ls")
    remote_files = []
    for file in _remote_files:
        file = file.strip()
        if file.endswith(end) or end == "":
            remote_files.append(file)
    return remote_files


def remove_end(file_list):
    new_file_list = []
    if file_list == None:
        return new_file_list
    for file in file_list:
        if "." in file:
            file = file.split(".")[0]
            new_file_list.append(file)
    return new_file_list


def init_ssh(host_name, port, user_name, password, source_sh=False):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 加载系统主机密钥,需要在连接服务器前执行该命令
    ssh.load_system_host_keys()
    # 连接服务器
    print(f"connecting to {host_name}:{port}...")
    ssh.connect(host_name, port, user_name, password)
    if source_sh:
        exec_cmd(ssh, "source /opt/intel/intel2019u5.sh")
    return ssh


def init_sftp(host_name, port, user_name, password):
    # 连接远程服务器
    t = paramiko.Transport((host_name, port))
    print(f"connecting to {host_name}:{port} file server...")
    t.connect(username=user_name, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    return t, sftp


def sync_from_remote(ssh,ssh_sftp, remote_fem_path, local_fem_path,end,file_gap=1,start_idx = 0):

    os.makedirs(local_fem_path, exist_ok=True)
    local_files = get_file_list(local_fem_path, reverse=False, end=end)
    remote_files = get_remote_file_list(ssh, remote_fem_path, end=end)

    print(f"remote_files: {remote_files}")
    print("===============sync from remote============")
    local_files_n = remove_end(local_files)
    remote_files_n = remove_end(remote_files)

    diff_files_n = []
    if file_gap == -1:
        last_r_file = -1
        idx = 0
        last_r_file_idx = -1
        for r_file in remote_files_n:
            if int(r_file) > last_r_file:
                last_r_file = int(r_file)
                last_r_file_idx = idx
                idx += 1
        if last_r_file_idx != -1 and remote_files_n[last_r_file_idx] not in local_files_n:

            # print(f"last_r_file: {last_r_file} idx : {last_r_file_idx}")
            diff_files_n = [remote_files_n[last_r_file_idx]]
    else:
        for r_file in remote_files_n:
            if r_file not in local_files_n and int(r_file) % file_gap == 0 and int(r_file) >= start_idx:
                diff_files_n.append(r_file)

    print(f"diff_files_n: {diff_files_n}")
    c = input("continue?[Y/n]")
    if c != "y" and c != "":
        return []

    for file_n in diff_files_n:
        print(f"downloading from {remote_fem_path + '/' + file_n + end}")
        down_from_remote(ssh_sftp, remote_fem_path + '/' + file_n + end,
                         local_fem_path + '/' + file_n + end)
    return diff_files_n

def sync_to_remote(ssh, ssh_sftp,local_fem_path,remote_fem_path,end):
    print("===============sync to remote============")
    exec_cmd(ssh, f'mkdir -p {remote_fem_path}')
    local_files = get_file_list(local_fem_path, reverse=False, end=end)
    remote_files = get_remote_file_list(ssh, remote_fem_path, end=end)
    local_files_n = remove_end(local_files)
    remote_files_n = remove_end(remote_files)
    diff_files_n = []

    for r_file in local_files_n:
        if r_file not in remote_files_n:
            diff_files_n.append(r_file)
    print(f"diff_files_n: {diff_files_n}")
    for file_n in diff_files_n:
        print(f"uploading to {remote_fem_path + '/' + file_n + end}")
        upload_to_remote(ssh_sftp,local_fem_path + '/' + file_n + end,
                         remote_fem_path + '/' + file_n + end)
    return diff_files_n