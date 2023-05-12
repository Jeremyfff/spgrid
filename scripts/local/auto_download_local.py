import os

from auto_download import *
import atexit

if __name__ == "__main__":
    '''
    改代码会自动同步服务器内容并下载到本地
    '''
    # 远程文件路径（需要绝对路径）
    remote_dir = r'/hy-tmp/taichi/outputs/topo_opt/'
    # 本地文件存放路径（绝对路径或者相对路径都可以）
    local_dir = r'D:\M.Arch\2023Spr\DesignClass_ComputationalDesignandHigh-performance3DPrintingConstruction\Spgrid_topo_opt\outputs'

    # 服务器SSH信息（OMEN）
    host_name = '10.192.32.26'
    user_name = 'root'
    password = 'VQ*D?>fdb}u#,truQ]u+LYZx.0c_3~F2wvdeAAjHw:9TQ4rBxf>aaUt-+_jP!!XUpAgs#kD8bAj9ng*~UB>v!L75}GMxkpPaxQ~*'
    port = 36850

    # 连接服务器
    client = init_ssh(host_name, port, user_name, password)
    client_t, client_sftp = init_sftp(host_name, port, user_name, password)



    # 远程文件开始下载ps
    down_from_remote(client_sftp, '/hy-tmp/taichi/projects/spgrid/scripts/utils/ps.txt', 'ps.txt')

    remote_task_name_list , remote_task_path_list = Get_ps('ps.txt')
    print("\n\n")
    idx = 0
    for path in remote_task_path_list:
        print(str(idx) + ":" + path)
        idx += 1
    c = input("\nselect which one?")
    c = int(c)
    remote_task_path = remote_task_path_list[c]
    shared_path = Get_shared_path_byselect(remote_task_path)
    remote_task_name = remote_task_name_list[c]

    remote_task_path = os.path.join(remote_dir, shared_path)
    local_task_path = os.path.join(local_dir, shared_path)

    remote_fem_path = os.path.join(remote_task_path, "fem")
    local_fem_path = os.path.join(local_task_path, "fem")

    print(f"remote_fem_path: {remote_fem_path}")
    print(f"local_fem_path: {local_fem_path}")
    print("\n")
    #下载代码文件
    os.makedirs(local_task_path,exist_ok=True)
    #print(os.path.join(remote_task_path, remote_task_name + ".py"))
    down_from_remote(client_sftp, os.path.join(remote_task_path, remote_task_name), os.path.join(local_task_path, remote_task_name))
    # 从google cloud下载文件
    sync_from_remote(client,client_sftp,remote_fem_path,local_fem_path,".ply.zip",file_gap=1,start_idx=0)



    # 关闭连接
    client.close()
    #route.close()

    # 关闭连接
    client_t.close()
    #route_t.close()
    print("client closed")

@atexit.register
def clean():
    print("force exit, closing client")
    # 关闭连接
    client.close()
    # route.close()

    # 关闭连接
    client_t.close()
    # route_t.close()
