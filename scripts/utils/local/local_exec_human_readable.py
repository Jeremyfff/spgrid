# import yaml
#
# with open('human_readable.txt', 'r') as f:
#     data = yaml.safe_load(f)
#
#
import json
import os
import time

from tqdm import tqdm


def get_resolution(lines):
    for line in lines:
        if line.startswith("    resolution: "):
            tmp = line.split("[")[1]
            tmp = tmp.split("]")[0]
            di = tmp.split(",")
            di_x = (int)(di[0].strip())
            di_y = (int)(di[1].strip())
            di_z = (int)(di[2].strip())
            return di_x, di_y, di_z
    return 0, 0, 0


# 从方括号的文本中获取xyz值
def value_from_square_brackets(square_brackets):
    tmp = square_brackets.strip()[1:-1].split(",")
    x = int(tmp[0].strip())
    y = int(tmp[1].strip())
    z = int(tmp[2].strip())
    return x, y, z


# 从base_coordinates_line文本中获取base_coordinate
def get_base_coordinate(base_coordinates_line):
    square_brackets = base_coordinates_line.split(":")[1]
    x, y, z = value_from_square_brackets(square_brackets)
    base = (x, y, z)
    return base


def get_coord_value(line, base):
    tmp = line.split(":")
    _x, _y, _z = value_from_square_brackets(tmp[0])
    value = float(tmp[1].strip())
    coord = (_x + base[0], _y + base[1], _z + base[2])
    return coord, value


def exec_blocks(lines, prefix, file_path, threshold = 0.0):
    start_time = time.time()
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prefix)
        f.close()
    with open(file_path, 'a', encoding='utf-8') as f:
        block = 0
        vertices = 0
        for i in tqdm(range(len(lines))):
            if lines[i] == "      [" + str(block) + "]: {\n":
                # print(f"find block {block} : ")

                # 解析base coordinate
                base = get_base_coordinate(lines[i + 1])
                # print(f"base: {base}")
                for j in range(64):
                    coord, value = get_coord_value(lines[i + j + 2], base)
                    if value > threshold:
                        vertices += 1
                        # print(f"coord: {coord}  value: {value}")
                        f.write(f"{coord[0]} {coord[1]} {coord[2]} {value}\n")

                # print(f"block  {block} end")
                block += 1
                continue
    exec_time = time.time() - start_time

    print(f"complete | total vertivces {vertices} | time {exec_time} sec")

def count_blocks(lines):
    block = 0
    for i in range(len(lines)):
        if lines[i] == "      [" + str(block) + "]: {\n":
            block += 1
    return block


if __name__ == "__main__":
    with open('human_readable3.txt', 'r') as f:
        lines = f.readlines()

    print(len(lines))

    di_x, di_y, di_z = get_resolution(lines)
    print(f"di_x={di_x}, di_y={di_y}, di_z={di_z}")

    block_count = count_blocks(lines)
    print(f"block count {block_count}")
    prefix = f"ply\n" \
             f"format ascii 1.0\n" \
             f"comment author: Jeremy\n" \
             f"comment object: Topo\n" \
             f"element vertex {block_count * 64}\n" \
             f"property float x\n" \
             f"property float y\n" \
             f"property float z\n" \
             f"property float density\n" \
             f"end_header\n"

    exec_blocks(lines, prefix, "test3.ply", threshold=0.0)
