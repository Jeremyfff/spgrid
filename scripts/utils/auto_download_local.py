import os

from auto_download import *

if __name__ == "__main__":
    ply_mode = False

    # 远程文件路径（需要绝对路径）
    remote_dir = r'/hy-tmp/taichi/outputs/topo_opt/'
    # 本地文件存放路径（绝对路径或者相对路径都可以）
    local_dir = r'D:\M.Arch\2023Spr\DesignClass_ComputationalDesignandHigh-performance3DPrintingConstruction\Spgrid_topo_opt\outputs'
    route_dir = r'/hy-tmp/taichi/outputs/topo_opt/'

    file_gap = 1

    # 服务器连接信息
    #google cloud
    host_name = '34.68.133.28'
    user_name = 'root'
    password = 'fyh1999727'
    port = 22

    # 恒源云 （P4）
    route_name = 'i-2.gpushare.com'
    route_user_name = 'root'
    route_password = '8B3WFZnrzbwmVyXDa2qPwenAY75YNzzS'
    route_port = 48289

    client = init_ssh(host_name, port, user_name, password)
    client_t, client_sftp = init_sftp(host_name, port, user_name, password)

    route = init_ssh(route_name, route_port, route_user_name, route_password)
    route_t, route_sftp = init_sftp(route_name, route_port, route_user_name, route_password)



    # 远程文件开始下载ps
    down_from_remote(client_sftp, '/hy-tmp/taichi/projects/spgrid/scripts/utils/ps.txt', './ps.txt')

    shared_path = Get_shared_path(ps_path='./ps.txt')

    remote_task_path = os.path.join(remote_dir, shared_path)
    local_task_path = os.path.join(local_dir, shared_path)
    route_task_path = os.path.join(route_dir, shared_path)

    remote_fem_path = os.path.join(remote_task_path, "fem")
    local_fem_path = os.path.join(local_task_path, "fem")
    route_fem_path = os.path.join(route_task_path, "fem")

    print(f"remote_fem_path: {remote_fem_path}")
    print(f"local_fem_path: {local_fem_path}")
    print("\n")

    if not ply_mode:
        # 从google cloud下载文件
        sync_from_remote(client,client_sftp,remote_fem_path,local_fem_path,".tcb.zip",file_gap=1)

        # 上传ps到route 服务器
        upload_to_remote(route_sftp, "./ps.txt", '/hy-tmp/taichi/projects/spgrid/scripts/utils/ps.txt')

        # 上传文件到 route服务器
        diff_file_n = sync_to_remote(route,route_sftp,local_fem_path,route_fem_path,".tcb.zip")
        print("please manually process data on route server...")
    else:
        # 从route服务器下载ply文件
        sync_from_remote(route,route_sftp,remote_fem_path,local_fem_path,".ply",file_gap=1)


    #
    # route_files = get_remote_file_list(route, route_fem_path, end=".tcb.zip")
    # local_files = get_file_list(local_fem_path,end=".txt")
    # route_files_n = remove_end(route_files)
    # local_files_n = remove_end(local_files)
    #
    # for file_n in route_files_n:
    #     if len(local_files_n) > 0 and file_n in local_files_n:
    #         continue
    #     print(f"processing {file_n}...")
    #     print(f"unzipping {file_n}...")
    #     output1 = exec_cmd(route, f"cd {route_fem_path} && unzip -o {file_n + '.tcb.zip'}")
    #     print(f"converting {file_n} to txt...")
    #     # output2 = exec_cmd(route,f"sudo -i cd {route_fem_path} && source /opt/intel/intel2019u5.sh && ti run convert_fem_solve {route_fem_path}/{file_n}.tcb --with-density")
    #
    #     output2 = exec_cmd(route,
    #                        'echo %s | sudo -S %s' % (route_password, f"sudo -i cd {route_fem_path} && source /opt/intel/intel2019u5.sh && ti run convert_fem_solve {route_fem_path}/{file_n}.tcb --with-density"))
    #
    #
    #     exec_cmd(route, f"cd {remote_fem_path} && mv human_readable.txt {file_n}.txt")
    #     exec_cmd(route, f"cd {remote_fem_path} && rm {file_n}.tcb")
    #     print(f"downloading {file_n}...")
    #     down_from_remote(route_sftp,f"{route_fem_path}/{file_n}.txt", f"{local_fem_path}/{file_n}.txt")
    #
    # # sync files once
    # # 1. download .tcb.zip







    #
    #
    # # start transforming
    # for file_name in target_files_names:
    #     if file_name not in remote_files_names_tcb and file_name not in remote_files_names_txt:
    #         output = exec_cmd(client, f"cd {remote_fem_path} && unzip -o {file_name + '.tcb.zip'}")
    #         print(f"unziping {file_name}.tcb.zip")
    #     else:
    #         print(f"find unzipped file {file_name}")
    #
    #     if file_name not in remote_files_names_txt:
    #         output = exec_cmd(client,
    #                           f"cd {remote_fem_path} && ti run convert_fem_solve {remote_fem_path}/{file_name}.tcb --with-density")
    #         for line in output:
    #             print(line)
    #
    #         org_path = f"{remote_fem_path}/human_readable.txt"
    #         new_path = f"{remote_fem_path}/{file_name}.txt"
    #         exec_cmd(client, f"cd {remote_fem_path} && mv human_readable.txt {file_name}.txt")
    #         exec_cmd(client, f"cd {remote_fem_path} && rm {file_name}.tcb")

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
    route.close()

    # 关闭连接
    client_t.close()
    route_t.close()
