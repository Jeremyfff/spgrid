import datetime
import threading
import time
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import filedialog
from tqdm import tqdm
import configparser
from auto_download import *
import io
from tkinter import messagebox
from PIL import ImageTk, Image
import zipfile
import numpy as np
import polyscope as ps
import imgui_custom
import atexit
import utils
import datatable as dt
# IMPORTANT: MUST READ BEFORE RUNNING
# Please modify the server and other configuration information in config.ini
# Set your server password in system environment variable or config.ini
# I set the variable name in the system environment to OMEN_PWD,
# you can also change it to your own variable name

config = configparser.ConfigParser()
config.read('./config.ini')
host_name = config.get('Server', 'host_name')
port = config.getint('Server', 'port')
user_name = config.get('Server', 'user_name')
password = config.get('Server', 'password')
if password == "":
    password = os.environ.get("OMEN_PWD")
    assert password is not None
remote_dir = config.get('Path', 'remote_dir')
local_dir = config.get('Path', 'local_dir')


class Application(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.image = None
        self.master = master
        self.grid()
        self.create_widgets()

        self.columnconfigure(0, minsize=180)

        self.columnconfigure(1, minsize=320)
        self.columnconfigure(2, minsize=100)
        self.columnconfigure(3, minsize=100)

    def create_widgets(self):
        # 创建打开文件夹按钮
        self.label1 = ttk.Label(self, textvariable=cs)
        self.label1.grid(row=0, column=0, pady=5, sticky="n")

        self.button1 = ttk.Button(self, text="连接服务器", command=self.connect_server, bootstyle="default")
        self.button1.grid(row=1, column=0, pady=5, sticky="nsew")

        self.button2 = ttk.Button(self, text="刷新任务", command=self.refresh_solvers, state='disabled',
                                  bootstyle="secondary")
        self.button2.grid(row=2, column=0, pady=5, sticky="nsew")

        self.button3 = ttk.Button(self, text="同步文件", command=self.sync_with_server, state='disabled',
                                  bootstyle="success")
        self.button3.grid(row=3, column=0, pady=5, sticky="nsew")

        self.button4 = ttk.Button(self, text="下载文件", command=self.download_from_server, state='disabled',
                                  bootstyle="success")
        self.button4.grid(row=4, column=0, pady=5, sticky="nsew")

        self.button5 = ttk.Button(self, text="打开本地文件夹", command=self.open_folder, state='disabled',
                                  bootstyle="secondary")
        self.button5.grid(row=5, column=0, pady=5, sticky="nsew")
        self.button6 = ttk.Button(self, text="处理文件", command=self.open_window, state='normal', bootstyle="default")
        self.button6.grid(row=6, column=0, pady=5, sticky="nsew")

        # 占位符
        self.label_void = ttk.Label(self, text=" ")
        self.label_void.grid(row=8, column=0, pady=50)

        # 创建进度条
        self.label2 = ttk.Label(self, text="整体进度:")
        self.label2.grid(row=9, column=0, pady=5)
        self.progressbar = ttk.Progressbar(self, mode="determinate")
        self.progressbar.grid(row=9, column=1, pady=2, padx=5, columnspan=2, sticky="nsew")

        self.button_cancle = ttk.Button(self, text="取消", command=self.cancle_download)
        self.button_cancle.grid(row=9, column=3, pady=5, padx=5, rowspan=2, sticky="nsew")

        self.label2 = ttk.Label(self, textvariable=cs2)
        self.label2.grid(row=10, column=0, pady=5)
        self.progressbar2 = ttk.Progressbar(self, mode="determinate")
        self.progressbar2.grid(row=10, column=1, pady=2, padx=5, columnspan=2, sticky="nsew")
        self.progressbar2['maximum'] = 100

        # 创建文件列表框
        self.listbox = tk.Listbox(self)
        self.listbox.grid(row=1, column=1, rowspan=8, pady=5, padx=5, sticky="nsew")
        # 绑定Listbox的选中事件到回调函数上
        self.listbox.bind('<<ListboxSelect>>', self.on_listbox_select)

        # 创建文件列表框
        self.listbox2 = tk.Listbox(self, selectmode=tk.EXTENDED)
        self.listbox2.grid(row=1, column=2, rowspan=8, pady=5, padx=5, sticky="nsew")

        self.output_text = tk.Text(self, height=10, width=40)
        self.output_text.grid(row=1, column=3, rowspan=8, pady=5, padx=5, sticky="nsew")

    def connect_server(self):
        # 连接服务器
        global client, client_t, client_sftp
        cs.set("连接中...")
        with io.StringIO() as buffer:
            # 重定向stdout到字符串缓冲区
            sys.stdout = buffer

            client = init_ssh(host_name, port, user_name, password)
            client_t, client_sftp = init_sftp(host_name, port, user_name, password)

            sys.stdout = sys.__stdout__
            # 显示函数输出
            self.output_text.insert("end", buffer.getvalue())
            self.output_text.yview_moveto(1.0)
            cs.set(f"服务器已连接 {host_name}")
        self.refresh_solvers()
        self.button2['state'] = 'normal'
        self.button3['state'] = 'normal'

    def refresh_solvers(self):
        global remote_task_name_list, remote_task_path_list
        if client is None:
            messagebox.showinfo("Information", "PLEASE CONNECT SERVER FIRST")
            return

        self.output_text.insert("end", "正在下载文件: ps.txt\n")
        self.output_text.yview_moveto(1.0)
        down_from_remote(client_sftp, '/hy-tmp/taichi/projects/spgrid/scripts/utils/ps.txt', 'ps.txt')

        remote_task_name_list, remote_task_path_list = Get_ps('ps.txt')
        idx = 0
        self.listbox.delete(0, tk.END)
        for path in remote_task_path_list:
            line = f"{idx} : {os.path.basename(path)}"
            idx += 1
            self.listbox.insert(tk.END, line)
        self.output_text.insert("end", "solvers列表已更新\n")
        self.output_text.yview_moveto(1.0)

    def on_listbox_select(self, event):
        if len(event.widget.curselection()) == 0:
            return
        self.sync_with_server()

    def sync_with_server(self, showInfo=True):
        # 获得与服务器不同的文件
        global client
        if client is None:
            if showInfo:
                messagebox.showinfo("Information", "PLEASE CONNECT SERVER FIRST")
            return
        if len(self.listbox.curselection()) > 0:
            c = self.listbox.curselection()[0]
        else:
            if showInfo:
                messagebox.showinfo("Information", "Please select a solver")
            return
        global remote_task_path_list, remote_task_path_list, remote_task_path, local_task_path, remote_fem_path, local_fem_path

        remote_task_path = remote_task_path_list[c]
        shared_path = Get_shared_path_byselect(remote_task_path)
        remote_task_name = remote_task_name_list[c]

        remote_task_path = os.path.join(remote_dir, shared_path)
        local_task_path = os.path.join(local_dir, shared_path)

        remote_fem_path = os.path.join(remote_task_path, "fem")
        local_fem_path = os.path.join(local_task_path, "fem")

        end = ".ply.zip"

        start_idx = 0

        if not os.path.exists(local_fem_path):
            local_files = []
            self.button5['state'] = 'disabled'
            self.button6['state'] = 'disabled'
        else:
            local_files = get_file_list(local_fem_path, reverse=False, end=end)
            self.button5['state'] = 'normal'
            self.button6['state'] = 'normal'
        remote_files = get_remote_file_list(client, remote_fem_path, end=end)

        print(f"remote_files: {remote_files}")
        print("===============sync from remote============")

        local_files_n = remove_end(local_files)
        remote_files_n = remove_end(remote_files)

        global diff_files_n
        diff_files_n = []
        for r_file in remote_files_n:
            if r_file not in local_files_n and int(r_file) % 1 == 0 and int(r_file) >= start_idx:
                diff_files_n.append(r_file)

        print(f"diff_files_n: {diff_files_n}")

        self.listbox2.delete(0, tk.END)
        for n in diff_files_n:
            self.listbox2.insert(tk.END, n)
        if len(diff_files_n) == 0:
            self.listbox2.insert(tk.END, "没有未同步的文件")
            self.button4['state'] = 'disabled'
        else:
            self.button4['state'] = 'normal'

    def download_from_server(self):
        global client, client_sftp
        global remote_task_path_list, remote_task_path_list, remote_task_path, local_task_path, remote_fem_path, local_fem_path
        global diff_files_n
        if client is None:
            messagebox.showinfo("Information", "PLEASE CONNECT SERVER FIRST")
            return

        if len(diff_files_n) == 0:
            messagebox.showinfo("Information", "no file to sync")
            return

        if len(self.listbox2.curselection()) == 0:
            selected_files = diff_files_n
        else:
            selected_files = [diff_files_n[i] for i in self.listbox2.curselection()]

        os.makedirs(local_fem_path, exist_ok=True)
        download_thread = DownloadThread(self, selected_files)
        download_thread.start()

    def cancle_download(self):
        global permit_download
        permit_download = False

    def print_test(self):
        with io.StringIO() as buffer:
            # 重定向stdout到字符串缓冲区
            sys.stdout = buffer
            print(f"hello world {datetime.datetime.now().strftime('%X')} ")
            sys.stdout = sys.__stdout__
            # 显示函数输出
            self.output_text.insert("end", buffer.getvalue())
            self.output_text.yview_moveto(1.0)

    def open_folder(self):
        global local_fem_path
        if local_fem_path == "":
            return
        if os.path.exists(local_fem_path):
            os.startfile(local_fem_path)
        else:
            messagebox.showinfo("Information", "folder not created yet")
            return

    def update_progress(self, folder_path):
        num_files = len(os.listdir(folder_path))
        if self.progressbar["value"] < num_files:
            self.progressbar["value"] += 1
            self.master.after(1000, lambda: self.update_progress(folder_path))

    def open_window(self):
        global local_fem_path
        self.window_local_fem_path = local_fem_path
        if local_fem_path == "":
            self.window_local_fem_path = filedialog.askdirectory()

        self.window = tk.Toplevel(self)
        self.window.geometry('1000x600')

        self.window.resizable(True, True)
        self.window.grid()

        button_width = 10
        path = self.window_local_fem_path
        if len(path) > 104:
            path = "..." + path[-100:-1] + path[-1]

        # title (file path)
        self.sub_label1 = ttk.Label(self.window, text=path)
        self.sub_label1.grid(row=0, column=0, pady=5, columnspan=4, sticky="nsew")

        # ==========================================LEFT===================================================
        # buttons
        self.sub_button1 = ttk.Button(self.window, text="解压", command=self.unzip_all, width=button_width,
                                      state='disabled')
        self.sub_button1.grid(row=1, column=0, columnspan=2, pady=5, sticky="nsew")

        self.sub_button2 = ttk.Button(self.window, text="生成预览图", command=self.generate_snapshots, state='disabled',
                                      width=button_width)
        self.sub_button2.grid(row=2, column=0, columnspan=2, pady=5, sticky="nsew")

        self.sub_button3 = ttk.Button(self.window, text="以polyscope打开", command=self.open_with_polyscope,
                                      state='disabled', width=button_width)
        self.sub_button3.grid(row=3, column=0, columnspan=2, pady=5, sticky="nsew")

        self.sub_button4 = ttk.Button(self.window, text="清空ply", command=self.clean_ply, state='normal',
                                      width=button_width)
        self.sub_button4.grid(row=4, column=0, pady=5, sticky="nsew")

        self.sub_button5 = ttk.Button(self.window, text="清空npy", command=self.clean_npy, state='normal',
                                      width=button_width)
        self.sub_button5.grid(row=4, column=1, pady=5, padx=1, sticky="nsew")

        self.sub_button6 = ttk.Button(self.window, text="刷新", command=self.update_listbox3, state='normal',
                                      width=button_width)
        self.sub_button6.grid(row=6, column=0, pady=5, columnspan=2, sticky="nsew")

        # --------------------------------settings---------------------------------------
        # point size
        temp_label = ttk.Label(self.window, text="point size")
        temp_label.grid(row=7, column=0, pady=5, sticky="nsew")
        self.entry_pointSize = tk.Entry(self.window)
        self.entry_pointSize.grid(row=7, column=1, pady=5, sticky="nsew")
        default_point_size = config.get('Polyscope', 'point_size')
        self.entry_pointSize.insert(0, default_point_size)

        # use cache
        self.var_use_cache = tk.BooleanVar()
        default_use_cache = config.getint('Polyscope', 'use_cache')
        self.var_use_cache.set(True if default_use_cache == 1 else False)
        self.checkbutton_use_cache = tk.Checkbutton(self.window, text="use_cache", variable=self.var_use_cache)
        self.checkbutton_use_cache.grid(row=8, column=0, pady=5, sticky="nsew")

        # save cache
        self.var_save_cache = tk.BooleanVar()
        default_save_cache = config.getint('Polyscope', 'save_cache')
        self.var_save_cache.set(True if default_save_cache == 1 else False)
        self.checkbutton_save_cache = tk.Checkbutton(self.window, text="save_cache", variable=self.var_save_cache)
        self.checkbutton_save_cache.grid(row=8, column=1, pady=5, sticky="nsew")

        # zoom factor
        temp_label = ttk.Label(self.window, text="zoom factor")
        temp_label.grid(row=9, column=0, pady=5, sticky="nsew")
        self.entry_zoom = tk.Entry(self.window)
        self.entry_zoom.grid(row=9, column=1, pady=5, sticky="nsew")
        zoom_factor = config.get('Polyscope', 'zoom_factor')
        self.entry_zoom.insert(0, zoom_factor)

        # z factor
        temp_label = ttk.Label(self.window, text="z factor")
        temp_label.grid(row=10, column=0, pady=5, sticky="nsew")
        self.entry_z = tk.Entry(self.window)
        self.entry_z.grid(row=10, column=1, pady=5, sticky="nsew")
        z_factor = config.get('Polyscope', 'z_factor')
        self.entry_z.insert(0, z_factor)

        # mirror
        temp_label = ttk.Label(self.window, text="mirror")
        temp_label.grid(row=11, column=0, pady=5, sticky="nsew")
        self.entry_mirror = tk.Entry(self.window)
        self.entry_mirror.grid(row=11, column=1, pady=5, sticky="nsew")
        mirror = config.get('Polyscope', 'mirror')
        self.entry_mirror.insert(0, mirror)

        # density threshold
        temp_label = ttk.Label(self.window, text="DensThresh")
        temp_label.grid(row=12, column=0, pady=5, sticky="nsew")
        self.entry_densThresh = tk.Entry(self.window)
        self.entry_densThresh.grid(row=12, column=1, pady=5, sticky="nsew")
        densThresh = config.get('Polyscope', 'densThresh')
        self.entry_densThresh.insert(0, densThresh)

        # save config
        self.sub_button_save = ttk.Button(self.window, text="保存配置", command=self.save_config, state='normal',
                                          width=button_width)
        self.sub_button_save.grid(row=13, column=0, pady=5, columnspan=2, sticky="nsew")

        # --------------------------------settings end---------------------------------------
        # blank
        temp_label_placement = ttk.Label(self.window, text="")
        temp_label_placement.grid(row=14, column=0, pady=20, columnspan=2, sticky="nsew")

        # ==========================================LEFT END===================================================

        # 创建文件列表框
        self.listbox3 = tk.Listbox(self.window, selectmode=tk.EXTENDED)
        self.listbox3.grid(row=1, column=2, rowspan=13, pady=5, padx=5, sticky="nsew")
        self.listbox3.bind('<<ListboxSelect>>', self.on_listbox3_select)

        self.image = Image.open('./test.png')
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(self.window, image=self.tk_image, width=600, height=400)
        self.image_label.grid(row=1, column=3, rowspan=13, pady=5, padx=5, sticky="nsew")

        self.update_listbox3()

    def save_config(self):
        config.set('Polyscope', 'point_size', self.entry_pointSize.get())
        config.set('Polyscope', 'use_cache', '1' if self.var_use_cache.get() else '0')
        config.set('Polyscope', 'save_cache', '1' if self.var_save_cache.get() else '0')
        config.set('Polyscope', 'zoom_factor', self.entry_zoom.get())
        config.set('Polyscope', 'z_factor', self.entry_z.get())
        config.set('Polyscope', 'mirror', self.entry_mirror.get())
        config.set('Polyscope', 'densThresh', self.entry_densThresh.get())
        with open('./config.ini', 'w') as f:
            config.write(f)

    def update_listbox3(self):
        ply_zips = get_file_list(self.window_local_fem_path, end=".ply.zip")
        plys = get_file_list(self.window_local_fem_path, end='.ply')
        npys = get_file_list(self.window_local_fem_path, end='.npy')
        pngs = get_file_list(self.window_local_fem_path, end='.png')
        n_ply_zips = remove_end(ply_zips)
        n_plys = remove_end(plys)
        n_npys = remove_end(npys)
        n_pngs = remove_end(pngs)

        y = self.listbox3.yview()[0]
        self.listbox3.delete(0, tk.END)

        n_union = list(set(n_ply_zips) | set(n_plys) | set(n_npys) | set(n_pngs))
        items: list[str] = []
        for n in n_union:
            has_ply_zip = True if n in n_ply_zips else False
            has_ply = True if n in n_plys else False
            has_npy = True if n in n_npys else False
            has_png = True if n in n_pngs else False
            line = f"{n}{' | ply' if has_ply else ''}{' | npy' if has_npy else ''}{' | png' if has_png else ''}"
            # self.listbox3.insert(tk.END, line)
            items.append(line)

        items.sort()
        for i in items:
            self.listbox3.insert(tk.END, i)
        self.listbox3.yview_moveto(y)

    def unzip_all(self):
        for idx in self.listbox3.curselection():
            name = self.listbox3.get(idx).split("|")[0].strip()
            if os.path.exists(os.path.join(self.window_local_fem_path, f"{name}.ply")):
                print("ply already exist")
                continue
            zip_file = zipfile.ZipFile(os.path.join(self.window_local_fem_path, f"{name}.ply.zip"))
            for file in zip_file.namelist():
                zip_file.extract(file, self.window_local_fem_path)  # 解压位置
            zip_file.close()
        self.update_listbox3()

    def clean_ply(self):
        ply_zips = get_file_list(self.window_local_fem_path, end='.ply.zip')
        if len(self.listbox3.curselection()) == 0:
            plys = get_file_list(self.window_local_fem_path, end='.ply')
        else:
            plys = [f"{self.listbox3.get(i).split('|')[0].strip()}.ply" for i in self.listbox3.curselection()]
        n_ply_zips = remove_end(ply_zips)
        n_plys = remove_end(plys)
        for n in n_plys:
            if n not in n_ply_zips:
                print(f"cannot find ply.zip, skip {n}")
                continue
            path = os.path.join(self.window_local_fem_path, f"{n}.ply")
            if os.path.exists(path):
                os.remove(path)
        self.update_listbox3()

    def clean_npy(self):
        # clean npy file
        if len(self.listbox3.curselection()) == 0:
            npys = get_file_list(self.window_local_fem_path, end='.npy')
        else:
            npys = [f"{self.listbox3.get(i).split('|')[0].strip()}.npy" for i in self.listbox3.curselection()]
        for npy in npys:
            path = os.path.join(self.window_local_fem_path, npy)
            if os.path.exists(path):
                os.remove(path)
        self.update_listbox3()

    def general_action_for_polyscope(self, save_png=True, show=False, use_cache=True, save_cache=True):
        """
        some general actions for polyscope stuff, like open window or save snapshot
        :param save_png: whether to save snapshot
        :param show: whether to show in new window
        :param use_cache: whether to use cache
        :param save_cache: whether to save cache
        """
        # error check
        if len(self.listbox3.curselection()) == 0:
            return
        if len(self.listbox3.curselection()) > 1 and show:
            messagebox.showinfo("Information", "仅支持单选时打开")
            return

        self.init_polyscope()

        # copy current selection
        current_selection_indexes = list(self.listbox3.curselection()).copy()
        current_selection_names = [self.listbox3.get(i) for i in current_selection_indexes]

        # loop for each selection
        for name in current_selection_names:
            self.process_single_ply(name, save_png, show, use_cache, save_cache)  # process ply
        self.update_listbox3()  # update listbox after all Done

    def init_polyscope(self):
        global has_ps
        if not has_ps:
            # check if polyscope(ps) has already initialized
            # if not, initialize polyscope
            ps.set_program_name("SPgrid Preview")
            ps.set_autocenter_structures(True)
            ps.set_autoscale_structures(True)
            ps.set_user_callback(imgui_custom.callback)
            ps.set_up_dir('neg_z_up')
            ps.set_ground_plane_mode('none')

            ps.init()
            print("ps initialized")
            has_ps = True

    def process_single_ply(self, name: str, save_png: bool, show: bool, use_cache: bool, save_cache: bool) -> None:
        """
        process a single ply file
        :param name: file nmae
        :param save_png: whether to save snapshot
        :param show: whether to show in new window
        :param use_cache: whether to use cache
        :param save_cache: whether to save cache
        :return:
        """
        name = name.split("|")[0].strip()  # get pure name like 00010
        _local_fem_path = self.window_local_fem_path  #
        print(f"name = {name}")

        # if cache not exist or not use cache, and no ply file found, unzip ply.zip
        if (not os.path.exists(os.path.join(_local_fem_path, f"{name}.npy"))) or not use_cache:
            if not os.path.exists(os.path.join(_local_fem_path, f"{name}.ply")):
                zip_file = zipfile.ZipFile(os.path.join(_local_fem_path, f"{name}.ply.zip"))
                for file in zip_file.namelist():
                    zip_file.extract(file, _local_fem_path)  # 解压位置
                zip_file.close()

        # get ply path
        path = os.path.join(_local_fem_path, f"{name}.ply")

        # load points
        points, p2idx = load_ply(path, use_cache=use_cache, save_cache=save_cache)  # p2idx is the short name for [
        # property to index]
        print("==============property : index=================")
        print(p2idx)

        file_name = os.path.basename(path)

        has_dis = 'f_x' in p2idx
        has_sum = 'sum' in p2idx

        # remove low density points
        try:
            densThresh = float(self.entry_densThresh.get())
        except Exception as e:
            print(e)
            densThresh = 0.05
        points: np.array = points[points[:, p2idx['density']] > densThresh]  # density threshold
        print(f"points.shape {points.shape}")

        # get bounds
        max_x = np.max(points[:, p2idx['x']])
        max_y = np.max(points[:, p2idx['y']])
        max_z = np.max(points[:, p2idx['z']])
        min_x = np.min(points[:, p2idx['x']])
        min_y = np.min(points[:, p2idx['y']])
        min_z = np.min(points[:, p2idx['z']])
        print(f"bound x:{min_x}~{max_x}, y:{min_y}~{max_y}, z:{min_z}~{max_z}")

        # process mirror behaviour
        # get rid of side points
        mirror = self.entry_mirror.get()
        if 'x' in mirror:
            points = points[points[:, p2idx['x']] < max_x]
        if 'y' in mirror:
            points = points[points[:, p2idx['y']] < max_y]
        if 'z' in mirror:
            points = points[points[:, p2idx['z']] < max_z]



        # get displacement
        min_dis, max_dis = 0, 0
        if has_dis:
            dis: np.array = np.sqrt(
                points[:, p2idx['f_x']] * points[:, p2idx['f_x']]
                + points[:, p2idx['f_y']] * points[:, p2idx['f_y']]
                + points[:, p2idx['f_z']] * points[:, p2idx['f_z']])
            points = np.hstack((points, dis[:, np.newaxis]))
            p2idx['dis'] = points.shape[1] - 1
            print(p2idx)
            min_dis = round(np.min(points[:,  p2idx['dis']]), 3)
            max_dis = round(np.max(points[:,  p2idx['dis']]), 3)
        # get sum
        min_sum, max_sum = 0, 0
        if has_sum:
            min_sum = round(np.min(points[:, p2idx['sum']]), 3)
            max_sum = round(np.max(points[:, p2idx['sum']]), 3)

        # update custom GUI
        if has_dis:
            imgui_custom.min_dis = min_dis
            imgui_custom.max_dis = max_dis
            print(f"min_dis: {min_dis}, max_dis: {max_dis}")
        else:
            imgui_custom.min_dis = 0
            imgui_custom.max_dis = 0

        if 'x' in mirror:
            x_mirror = points.copy()
            x_mirror[:, p2idx['x']] = 2 * max_x - 1 - points[:, p2idx['x']]
            points = np.vstack((points, x_mirror))
        if 'y' in mirror:
            y_mirror = points.copy()
            y_mirror[:, p2idx['y']] = 2 * max_y - 1 - points[:, p2idx['y']]
            points = np.vstack((points, y_mirror))
        if 'z' in mirror:
            z_mirror = points.copy()
            z_mirror[:, p2idx['z']] = 2 * max_z - 1 - points[:, p2idx['z']]
            points = np.vstack((points, z_mirror))

        # generate point cloud
        try:
            point_size = float(self.entry_pointSize.get())
        except Exception as e:
            print(e)
            point_size = 0.005

        ps_cloud = ps.register_point_cloud(file_name, points[:,  p2idx['x']:p2idx['z']+1], point_render_mode='sphere', radius=point_size,
                                           color=(0.7, 0.7, 0.7))

        # set camera
        try:
            zoom_factor = float(self.entry_zoom.get())
        except Exception as e:
            print(e)
            zoom_factor = 1
        zoom_factor = 1 if zoom_factor == 0 else zoom_factor
        try:
            z_factor = float(self.entry_z.get())
        except Exception as e:
            print(e)
            z_factor = 1
        print(f"zoom factor = {zoom_factor}")
        ps.look_at((-0.8 / zoom_factor, 0.8 / zoom_factor, 0.8 / zoom_factor * z_factor), (0, 0, 0))

        # register displacement
        if has_dis:
            ps_cloud.add_scalar_quantity("displacement", points[:, p2idx['dis']], vminmax=(min_dis, max_dis), cmap="jet",
                                         enabled=False)

        # register sum value
        if has_sum:
            ps_cloud.add_scalar_quantity("sum", points[:, p2idx['sum']], vminmax=(min_sum, max_sum), cmap="jet", enabled=False)

        # save snapshot
        if save_png:
            ps.screenshot(os.path.join(_local_fem_path, f"{name}.png"), transparent_bg=True)

        # show window
        if show:
            ps.show()  # program will stack here

        # exit function
        ps_cloud.remove()  # remove point cloud
        self.update_listbox3()  # update listbox
        self.update()  # redraw ui

    def generate_snapshots(self):
        idx = self.listbox3.curselection()[0]
        self.general_action_for_polyscope(save_png=True, show=False, use_cache=self.var_use_cache.get(),
                                          save_cache=self.var_save_cache.get())
        # snapshot_thread = GetSnapshotThread(self,True,False,True,True)
        # snapshot_thread.start()
        self.listbox3.select_set(idx)
        self.update_image()

    def open_with_polyscope(self):
        self.general_action_for_polyscope(save_png=False, show=True, use_cache=self.var_use_cache.get(),
                                          save_cache=self.var_save_cache.get())

    def on_listbox3_select(self, event):
        if len(event.widget.curselection()) == 0:
            self.sub_button1['state'] = 'disabled'
            self.sub_button2['state'] = 'disabled'
            self.sub_button3['state'] = 'disabled'
            return
        self.sub_button1['state'] = 'normal'
        self.sub_button2['state'] = 'normal'
        self.sub_button3['state'] = 'normal'
        self.update_image()

    def update_image(self):
        """
        update the image
        :return:
        """
        if len(self.listbox3.curselection()) == 0:
            return
        index = self.listbox3.curselection()[0]
        name = self.listbox3.get(index).split("|")[0].strip()  # get pure name like 00010
        png_path = os.path.join(self.window_local_fem_path, f"{name}.png")
        if os.path.exists(png_path):
            self.image = Image.open(png_path)
            w_box = 600
            h_box = 400
            w, h = self.image.size
            self.image = resize(w, h, w_box, h_box, self.image)
            # convert image to tk image
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.image_label = tk.Label(self.window, image=self.tk_image, width=600, height=400)
            self.image_label.grid(row=1, column=3, rowspan=13, pady=5, padx=5, sticky="nsew")  # consistent with above
            print("image updated")


class DownloadThread(threading.Thread):

    def __init__(self, app, selected_files):
        threading.Thread.__init__(self)
        self.app = app
        self.selected_files = selected_files

    def run(self):
        global permit_download
        permit_download = True
        end = ".ply.zip"
        count = 0
        self.app.progressbar['maximum'] = len(self.selected_files)
        for file_n in self.selected_files:
            if not permit_download:
                print("user cancel")
                break
            count += 1
            app.progressbar['value'] = count
            cs2.set(file_n)
            print(f"downloading from {remote_fem_path + '/' + file_n + end}")
            down_from_remote(client_sftp, remote_fem_path + '/' + file_n + end,
                             local_fem_path + '/' + file_n + end, callback=download_callback)

        app.sync_with_server()  # refresh file list after download


def download_callback(transferred, toBeTransferred, suffix='') -> None:
    """
    Callback function when the download update progress is updated
    """
    # written by chatGPT
    bar_len = 100
    filled_len = int(round(bar_len * transferred / float(toBeTransferred)))
    percents = round(100.0 * transferred / float(toBeTransferred), 1)
    bar = "\r[" + "".join(["=" for i in range(filled_len)]) + "".join(
        [" " for i in range(bar_len - filled_len)]) + f"] {percents}%"
    print(bar, end="")
    # written by chatGPT end
    app.progressbar2['value'] = int(percents)


class GetSnapshotThread(threading.Thread):
    """
    Using threads causes OpenGL errors, it is not used in this project.
    """

    def __init__(self, app, save_png=True, show=False, use_cache=True, save_cache=True):
        threading.Thread.__init__(self)
        self.app = app
        self.save_png = save_png
        self.show = show
        self.use_cache = use_cache
        self.save_cache = save_cache

    def run(self):
        app.general_action_for_polyscope(save_png=self.save_png, show=self.show, use_cache=self.use_cache,
                                         save_cache=self.save_cache)


def load_ply(path: str, save_cache: bool = True, use_cache: bool = True) -> (np.array, dict):
    """
    load ply file from numpy array
    :param path: file path for .ply
    :param save_cache: whether to save cache (.npy)
    :param use_cache: whether to use cache (.npy)
    :return: data in numpy array format
    """

    properties: list = []
    propertie2idx: dict = {}

    start_time = time.time()
    suffix: str = os.path.basename(path).split(".")[0]
    dir_name: str = os.path.dirname(os.path.abspath(path))
    npy_path: str = os.path.join(dir_name, f'{suffix}.npy')

    # load from file
    with open(path) as f:
        element_vertex: int = 0
        # properties: list = []
        while True:
            _line: str = f.readline()

            if _line == "end_header\n":
                break
            if _line.startswith("element vertex"):
                element_vertex = int(_line.strip().split(" ")[-1])

            if _line.startswith("property"):
                prop: str = _line.strip().split(" ")[-1]
                properties.append(prop)

        for i in range(len(properties)):
            propertie2idx[properties[i]] = i

        print(
            f'init complete\nelement_vertex count: {element_vertex}\nproperties count: {len(properties)}\n{properties}')

        # fast path
        if use_cache and os.path.exists(npy_path):
            print(f"use cached file {npy_path}")

            return np.load(npy_path), propertie2idx


        _points = np.empty(shape=(element_vertex, len(properties)))

        for i in tqdm(range(element_vertex), desc="loading data"):
            _line: str = f.readline()
            if _line == "":
                print(f"reach end early, i = {i}")
                _points = _points[:i, :]
                break
            data: list = _line.strip().split(" ")
            for j in range(len(properties)):
                _points[i][j] = float(data[j])

        print(f"shape = {_points.shape}")

        # save npy
        if save_cache:
            np.save(npy_path, _points)
            print(f"save cache to {npy_path}, note: this will take up a lot of space, delete it when not need")

        end_time = time.time()
        print(f"load time(vanilla python): {end_time - start_time}s")
        return _points, propertie2idx


def load_ply_fast(path: str, save_cache: bool = True, use_cache: bool = True) -> np.array:
    """
    The speed improvement of this method is limited, and the file saving function has temporary problems.
    ** do not use it **
    :param path: file path
    :param save_cache: whether to save cache (.npy)
    :param use_cache: whether to use cache (.npy)
    :return: data in numpy array format
    """
    suffix: str = os.path.basename(path).split(".")[0]
    dir_name: str = os.path.dirname(os.path.abspath(path))
    npy_path: str = os.path.join(dir_name, f'{suffix}.npy')

    # fast path
    if use_cache and os.path.exists(npy_path):
        print(f"use cached file {npy_path}")
        return np.load(npy_path)

    # load from file
    data = np.nan
    try:
        print("loading data...")
        data = np.loadtxt(path, dtype='float', encoding='utf-8', skiprows=0,
                          comments=['ply', 'format', 'comment', 'element', 'property', 'end_header'])  # 导入数据文
    except Exception as e:
        print(e)
        exit()

    print(f"shape = {data.shape}")
    # save npy
    if save_cache:
        with open(npy_path, 'wb') as f:
            f.write(data.tobytes())
        print(f"save cache to {npy_path}, note: this will take up a lot of space, delete it when not need")

    return data


def load_ply_cython(path: str, save_cache: bool = True, use_cache: bool = True) -> np.array:
    return utils.load_ply_vanilla(path, save_cache, use_cache)


def get_filesize(path):
    fsize = os.path.getsize(path)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


def get_filesizes(file_list, root_dir):
    size = 0.0
    for file in file_list:
        size += get_filesize(os.path.join(root_dir, file))
    return size


def resize(w, h, w_box, h_box, pil_image):
    '''
  resize a pil_image object so it will fit into
  a box of size w_box times h_box, but retain aspect ratio
  对一个pil_image对象进行缩放，让它在一个矩形框内，还能保持比例
  '''
    f1 = 1.0 * w_box / w  # 1.0 forces float division in Python2
    f2 = 1.0 * h_box / h
    factor = min([f1, f2])
    # print(f1, f2, factor) # test
    # use best down-sizing filter
    width = int(w * factor)
    height = int(h * factor)
    return pil_image.resize((width, height), Image.ANTIALIAS)


def close_client():
    global client
    if client is not None:
        client.close()
        client_t.close()
        print("client closed at exit")
    else:
        print("no client, safe exit")


def init():
    global app, root, style, cs, cs2, client, client_t, client_sftp, remote_task_name_list, remote_task_path_list
    global remote_task_path, local_task_path, remote_fem_path, local_fem_path, diff_files_n, permit_download, has_ps

    atexit.register(close_client)
    # create main window
    root = tk.Tk()
    root.geometry("1000x480")
    root.resizable(True, True)
    style = ttk.Style("darkly")

    # global var
    cs = tk.StringVar()
    cs.set("服务器未连接")
    cs2 = tk.StringVar()
    cs2.set("")
    client = None
    client_t = None
    client_sftp = None
    remote_task_name_list = []
    remote_task_path_list = []
    remote_task_path = ""
    local_task_path = ""
    remote_fem_path = ""
    local_fem_path = ""
    diff_files_n = []
    permit_download = True
    has_ps = False

    # create application
    root.call('tk', 'scaling', 1.5)  # If you encounter problems such as too large or too small display ratio,
                                     # please adjust this value
    app = Application(master=root)
    app.master.title("SPGrid TopoOpt Local File Manager")


def run():
    # run application
    global app
    app.mainloop()


def main_func():

    init()
    run()


if __name__ == "__main__":
    main_func()

