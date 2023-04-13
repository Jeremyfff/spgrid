"""
通过paramiko从远处服务器下载文件资源到本地
author: gxcuizy
time: 2018-08-01
"""

import paramiko
import os
from stat import S_ISDIR as isdir


def down_from_remote(sftp_obj, remote_dir_name, local_dir_name):
    """远程下载文件"""
    remote_file = sftp_obj.stat(remote_dir_name)
    if isdir(remote_file.st_mode):
        # 文件夹，不能直接下载，需要继续循环
        check_local_dir(local_dir_name)
        print('开始下载文件夹：' + remote_dir_name)
        for remote_file_name in sftp.listdir(remote_dir_name):
            sub_remote = os.path.join(remote_dir_name, remote_file_name)
            sub_remote = sub_remote.replace('\\', '/')
            sub_local = os.path.join(local_dir_name, remote_file_name)
            sub_local = sub_local.replace('\\', '/')
            down_from_remote(sftp_obj, sub_remote, sub_local)
    else:
        # 文件，直接下载
        print('开始下载文件：' + remote_dir_name)
        sftp.get(remote_dir_name, local_dir_name)


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


def Get_ps():
    ps = {}
    with open("./ps.txt", "r", encoding='utf-8') as f:
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


if __name__ == "__main__":

    # 远程文件路径（需要绝对路径）
    remote_dir = r'/hy-tmp/taichi/outputs/topo_opt/'
    # 本地文件存放路径（绝对路径或者相对路径都可以）
    local_dir = r'D:\M.Arch\2023Spr\DesignClass_ComputationalDesignandHigh-performance3DPrintingConstruction\Spgrid_topo_opt\outputs'

    

    file_gap = 5

    # 服务器连接信息
    host_name = '34.28.235.205'
    user_name = 'root'
    password = 'fyh1999727'
    port = 22

    client = paramiko.SSHClient()
    # 加载系统主机密钥,需要在连接服务器前执行该命令
    client.load_system_host_keys()
    # 连接服务器
    print("connecting server...")
    client.connect(host_name, port, user_name, password)
    output = exec_cmd(client, "source /opt/intel/intel2019u5.sh")
    # 连接远程服务器
    t = paramiko.Transport((host_name, port))
    print("connecting file server...")
    t.connect(username=user_name, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)

    # 远程文件开始下载ps
    down_from_remote(sftp, '/hy-tmp/taichi/projects/spgrid/scripts/utils/ps.txt', './ps.txt')

    ps = Get_ps()
    pths = []
    for v in ps.values():
        pths.append(v)
    remote_task_path = pths[0]
    _shared_path = remote_task_path.split("/")
    shared_path = _shared_path[-2] + "/" + _shared_path[-1] + "/"
    print(f"shared_path: {shared_path}")
    remote_task_path = os.path.join(remote_dir, shared_path)
    local_task_path = os.path.join(local_dir, shared_path)
    remote_fem_path = os.path.join(remote_task_path, "fem")
    local_fem_path = os.path.join(local_task_path, "fem")

    print(f"remote_fem_path: {remote_fem_path}")
    print(f"local_fem_path: {local_fem_path}")
    print("\n")

    os.makedirs(local_fem_path, exist_ok=True)

    # sync files
    local_files = get_file_list(local_fem_path, reverse=False, end=".ply")
    print(f"local_files: {local_files}")
    remote_files = get_remote_file_list(client, remote_fem_path, end=".tcb.zip")
    remote_files_tcb = get_remote_file_list(client, remote_fem_path, end=".tcb")
    remote_files_txt = get_remote_file_list(client, remote_fem_path, end=".txt")

    print(f"remote_files: {remote_files}")
    print(f"remote_files_tcb: {remote_files_tcb}")
    print(f"remote_files_txt: {remote_files_txt}")

    local_files_names = remove_end(local_files)
    remote_files_names = remove_end(remote_files)
    remote_files_names_tcb = remove_end(remote_files_tcb)
    remote_files_names_txt = remove_end(remote_files_txt)

    target_files_names = []
    for r_file in remote_files_names:
        if r_file not in local_files_names and int(r_file) % file_gap == 0:
            target_files_names.append(r_file)
    print(f"target_files_names: {target_files_names}")

    # start transforming
    for file_name in target_files_names:
        if file_name not in remote_files_names_tcb and file_name not in remote_files_names_txt:
            output = exec_cmd(client, f"cd {remote_fem_path} && unzip -o {file_name + '.tcb.zip'}")
            print(f"unziping {file_name}.tcb.zip")
        else:
            print(f"find unzipped file {file_name}")

        if file_name not in remote_files_names_txt:
            output = exec_cmd(client,
                              f"cd {remote_fem_path} && ti run convert_fem_solve {remote_fem_path}/{file_name}.tcb --with-density")
            for line in output:
                print(line)

            org_path = f"{remote_fem_path}/human_readable.txt"
            new_path = f"{remote_fem_path}/{file_name}.txt"
            exec_cmd(client,f"cd {remote_fem_path} && mv human_readable.txt {file_name}.txt")
            exec_cmd(client,f"cd {remote_fem_path} && rm {file_name}.tcb")

    # # user select fem path
    # fem_path = remote_dir
    # while True:
    #     print(fem_path)
    #     if fem_path.endswith(".tcb.zip") or fem_path.endswith(".tcb") or fem_path.endswith(".txt") or fem_path.endswith(".ply"):
    #         break
    #
    #     output = exec_cmd(client, f"cd {fem_path} && ls")
    #     msg = ""
    #     i = 0
    #     for file in output:
    #         msg += f"[{i}] {file.strip()}\n"
    #         i += 1
    #     msg += "[enter]select  [..]back\n"
    #     msg += "[user]: "
    #     c = input(msg)
    #     if c == "":
    #         break
    #     elif c == "..":
    #         s = fem_path.split("/")
    #         s = s[0:-2]
    #         new_fem_path = ""
    #         for ss in s:
    #             new_fem_path += ss + "/"
    #         fem_path = new_fem_path
    #     else:
    #         try:
    #             c = int(c)
    #             file = output[c].strip()
    #             if file.endswith(".tcb.zip") or file.endswith(".tcb") or file.endswith(".txt") or file.endswith(".ply"):
    #                 fem_path += file
    #                 break
    #             else:
    #                 fem_path += file + "/"
    #
    #         except Exception as e:
    #             print(e)
    #
    # print(f"final fem path: {fem_path}")

    # 关闭连接
    client.close()

    # 关闭连接
    t.close()
