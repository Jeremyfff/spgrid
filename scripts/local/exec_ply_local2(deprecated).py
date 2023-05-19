import os

import numpy as np
import polyscope as ps
# generating random 3D Points
from tqdm import tqdm
import imgui_custom

"""
早期测试代码，仅实现简单的打开并预览某个ply文件的功能。
其中许多代码已被替换为更新版本。
您应该使用auto_download_gui中的功能替代他
"""
def load_ply(path: str, save_cache: bool = True, use_cache: bool = True) -> np.array:
    suffix: str = os.path.basename(path).split(".")[0]
    dir_name: str = os.path.dirname(os.path.abspath(path))
    npy_path: str = os.path.join(dir_name, f'{suffix}.npy')

    # fast path
    if use_cache and os.path.exists(npy_path):
        print(f"use cached file {npy_path}")
        return np.load(npy_path)

    # load from file
    with open(path) as f:
        element_vertex: int = 0
        properties: list = []
        while True:
            _line: str = f.readline()

            if _line == "end_header\n":
                break
            if _line.startswith("element vertex"):
                element_vertex = int(_line.strip().split(" ")[-1])

            if _line.startswith("property"):
                prop: str = _line.strip().split(" ")[-1]
                properties.append(prop)

        print(
            f'init complete\nelement_vertex count: {element_vertex}\nproperties count: {len(properties)}\n{properties}')
        _points = np.empty(shape=(element_vertex, len(properties)))

        for i in tqdm(range(element_vertex), desc="loading data"):
            _line: str = f.readline()
            if _line == "":
                print(f"reach end, i = {i}")
                _points = _points[:i, :]
                break
            data: list = _line.strip().split(" ")
            for j in range(len(properties)):
                _points[i][j] = float(data[j])

        print(_points)
        print(f"shape = {_points.shape}")

        # save npy
        if save_cache:
            np.save(npy_path, _points)
            print(f"save cache to {npy_path}, note: this will take up a lot of space, delete it when not need")

        return _points


def remove_err_points(_points: np.array) -> np.array:
    _max_dis = np.max(_points[:, 7])
    _points_sub = _points[_points[:, 7] < _max_dis]
    _sub_max_dis = np.max(_points_sub[:, 7])
    print(_max_dis)
    print(_sub_max_dis)
    return _points


if __name__ == "__main__":
    path = "00200.ply"
    remove_err = False

    # load points
    points: np.array = load_ply(path)
    file_name = os.path.basename(path)

    # remove low density points
    points: np.array = points[points[:, 3] > 0.05]
    print(f"points.shape {points.shape}")

    # get displacement
    dis: np.array = np.sqrt(points[:, 4] * points[:, 4] + points[:, 5] * points[:, 5] + points[:, 6] * points[:, 6])
    points = np.hstack((points, dis[:, np.newaxis]))
    print(f"points: \n{points}")
    print(f"points.shape {points.shape}")

    # remove error points
    if remove_err:
        points = remove_err_points(points)

    # 0 | 1 | 2 | 3       | 4   | 5   | 6   | 7
    # x | y | z | density | f_x | f_y | f_z | dis

    # get bounds
    max_x = np.max(points[:, 0])
    max_y = np.max(points[:, 1])
    max_z = np.max(points[:, 2])
    min_x = np.min(points[:, 0])
    min_y = np.min(points[:, 1])
    min_z = np.min(points[:, 2])
    print(f"bound x:{min_x}~{max_x}, y:{min_y}~{max_y}, z:{min_z}~{max_z}")
    min_dis = round(np.min(points[:, 7]), 3)
    max_dis = round(np.max(points[:, 7]), 3)
    customGUI.min_dis = min_dis
    customGUI.max_dis = max_dis
    print(f"min_dis: {min_dis}, max_dis: {max_dis}")
    # #
    # points[:,7] = (points[:,7] - min_dis) / (max_dis - min_dis)

    # create color map
    # norm = matplotlib.colors.Normalize(vmin=min_dis, vmax=max_dis, clip=True)
    # mapper = cm.ScalarMappable(norm=norm, cmap=cm.turbo)
    # colors = mapper.to_rgba(points[:, 7])[:, 0:3]
    # print(colors)
    # print(colors.shape)

    # init
    ps.set_program_name("spgrid preview")
    ps.set_autocenter_structures(True)
    ps.set_autoscale_structures(True)
    ps.set_user_callback(customGUI.callback)
    ps.set_up_dir('neg_z_up')
    ps.set_ground_plane_mode('none')
    ps.init()
    ps_cloud = ps.register_point_cloud(file_name, points[:, 0:3], point_render_mode='sphere', radius=0.003)
    ps_cloud.add_scalar_quantity("displacement", points[:, 7], vminmax=(min_dis, max_dis), cmap="jet", enabled=True)
    ps.look_at((0.8, 0.8, 0.8), (0, 0, 0))
    ps.screenshot("test.png", transparent_bg=True)
    ps.show()

