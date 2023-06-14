import os
import subprocess

section = 3
max_frame = 10
SCRIPT_DIR = "/hy-tmp/taichi/projects/spgrid/scripts/"

OUTPUT_DIR_BASE = "/hy-tmp/taichi/outputs/topo_opt/floor_gh_0609_customHole/"

FRAME_FOLDER_BASE = f"customHole_sec{section}_frame_"

FINAL_OUTPUT_FOLDER = os.path.join(OUTPUT_DIR_BASE, f"customHole_sec{section}_animation")


def StrKwargs(kwargs):
    if kwargs is None:
        return ""
    kwargs = dict(kwargs)
    sufix = ""
    for key in kwargs:
        value = kwargs[key]
        sufix += f" --{key} {value}"
    return sufix


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


def ExecPy(fn, nohup=True, kwargs=None):
    if kwargs is None:
        kwargs = {}
    file_path = os.path.join(SCRIPT_DIR, fn)
    if nohup:
        cmd = f"nohup python3 {file_path}{StrKwargs(kwargs)} &"
        print(f"Executing: {cmd}")
        os.system(cmd)
    else:
        cmd = f"python3 {file_path}{StrKwargs(kwargs)}"
        print(f"Executing: {cmd}")
        os.system(cmd)



def ExecCmd(cmd: str, print_out: bool = False):
    r = os.popen(cmd)
    out = r.read()
    r.close()
    if print_out:
        print(out)
    return out


os.makedirs(FINAL_OUTPUT_FOLDER,exist_ok=True)
for i in range(max_frame + 1):
    print(f"###############Processing frame {i}#####################")
    frame_fem_path = os.path.join(OUTPUT_DIR_BASE, FRAME_FOLDER_BASE + str(i), "fem")
    tcb_zips = ListFiles(frame_fem_path, reverse=True, end=".tcb.zip", sort_type="name")
    last_file_name = tcb_zips[0]
    raw_file_name = last_file_name.replace(".tcb.zip", "")
    print(f"last file name: {last_file_name}   raw_file_name: {raw_file_name}")
    print(f"fem path: {frame_fem_path}")
    kwargs = {'block': 0, 'target': 2, 'file_list': last_file_name, 'fem_path': frame_fem_path}
    ExecPy(os.path.join(SCRIPT_DIR, 'utils/helper/exec_human_readable_legacy.py'), False, kwargs)

    org_path = os.path.join(frame_fem_path, f"{raw_file_name}.ply")
    new_path = os.path.join(FINAL_OUTPUT_FOLDER, f"frame_{i}.ply")
    ExecCmd(f"mv {org_path} {new_path}")

# file_list = []
# fem_paths = [""]
#
#
# kwargs = {'block': block, 'target': target, 'file_list': fib_str, 'fem_path': fem_path}
# task = ExecPy(os.path.join(SCRIPT_DIR, 'utils/helper/exec_human_readable_legacy.py'), False,kwargs)
