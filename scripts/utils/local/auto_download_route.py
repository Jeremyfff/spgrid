from auto_download import *

if __name__ == "__main__":
    # 远程文件路径（需要绝对路径）
    remote_dir = r'/hy-tmp/taichi/outputs/topo_opt/'
    # 本地文件存放路径（绝对路径或者相对路径都可以）
    #  local_dir = r'D:\M.Arch\2023Spr\DesignClass_ComputationalDesignandHigh-performance3DPrintingConstruction\Spgrid_topo_opt\outputs'
    local_dir = r'/hy-tmp/taichi/outputs/topo_opt/'

    file_gap = 1

    # 服务器连接信息
    host_name = '34.28.235.205'
    user_name = 'root'
    password = 'fyh1999727'
    port = 22

    client = init_client(host_name, port, user_name, password)
    t, sftp = init_sftp(host_name, port, user_name, password)

    # 远程文件开始下载ps
    down_from_remote(sftp, '/hy-tmp/taichi/projects/spgrid/scripts/utils/ps.txt', '../ps.txt')

    remote_task_path = Get_remote_task_path()

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

    # sync files once
    local_files = get_file_list(local_fem_path, reverse=False, end=".tcb.zip")
    remote_files = get_remote_file_list(client, remote_fem_path, end=".tcb.zip")


    print(f"remote_files: {remote_files}")

    local_files_names = remove_end(local_files)
    remote_files_names = remove_end(remote_files)

    target_files_names = []
    for remote_files_name in remote_files_names:
        if remote_files_name not in local_files_names and int(remote_files_name) % file_gap == 0:
            target_files_names.append(remote_files_name)
    print(f"target_files_names: {target_files_names}")

    for target_file_name in target_files_names:
        down_from_remote(sftp, os.path.join(remote_fem_path,target_file_name+".tcb.zip"),
                         os.path.join(local_fem_path,target_file_name + ".tcb.zip"))

    # 关闭连接
    client.close()

    # 关闭连接
    t.close()
