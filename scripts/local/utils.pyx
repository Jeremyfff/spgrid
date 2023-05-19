import numpy as np
import time
import os

import datatable as dt

from tqdm import tqdm
from libc.stdio cimport FILE, fopen, fclose, fgets
from libc.stdlib cimport atoi, strtod

def load_ply_vanilla(path: str, save_cache: bool = True, use_cache: bool = True) -> np.array:
    """
    load ply file from numpy array
    :param path: file path for .ply
    :param save_cache: whether to save cache (.npy)
    :param use_cache: whether to use cache (.npy)
    :return: data in numpy array format
    """
    start_time = time.time()
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
        return _points


# cdef extern from "stdio.h":
#     ctypedef FILE FILE_ptr
#     FILE_ptr fopen(const char *filename, const char *mode)
#     int fclose(FILE_ptr stream)
#     char *fgets(char *str, int num, FILE_ptr stream)

# cdef extern from "string.h":
#     ctypedef char *cstring
#     cstring strtok(char *str, const char *delim)



def load_ply_cython(path: str, save_cache: bool = True, use_cache: bool = True) -> np.array:
    # start_time = time.time()
    # suffix = os.path.basename(path).split(".")[0]
    # dir_name = os.path.dirname(os.path.abspath(path))
    # npy_path = os.path.join(dir_name, f'{suffix}.npy')
    #
    # # fast path
    # if use_cache and os.path.exists(npy_path):
    #     print(f"use cached file {npy_path}")
    #     return np.load(npy_path)
    #
    # cdef char* c_path = path.encode()
    # cdef FILE *file
    # cdef char* mode = "r"
    # cdef int MAX_LINE_LENGTH = 256
    # cdef char line[MAX_LINE_LENGTH]
    # file = fopen(c_path, mode)
    # if file == NULL:
    #     print("无法打开文件。\n")
    #     return None
    #
    # #逐行读取文件内容
    # while fgets(line, MAX_LINE_LENGTH, file):
    #     if strstr(line, "element") is not None:
    #         print("找到匹配的行: %s", line)
    #
    # fclose(file)
    # return None
    pass
    return None
