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
def float_from_square_brackets(square_brackets):
    tmp = square_brackets.strip()[1:-1].split(",")
    x = float(tmp[0].strip())
    y = float(tmp[1].strip())
    z = float(tmp[2].strip())
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


def exec_blocks2(f, prefix, file_path, threshold = 0.0):
    start_time = time.time()
    with open(file_path, 'w', encoding='utf-8') as ff:
        ff.write(prefix)
        ff.close()
    with open(file_path, 'a', encoding='utf-8') as ff:
        block = 0
        vertices = 0
        while True:
            line = f.readline()

            if line == "      [" + str(block) + "]: {\n":
                # print(f"find block {block} : ")

                # 解析base coordinate
                base = get_base_coordinate(f.readline())
                # print(f"base: {base}")
                for j in range(64):
                    coord, value = get_coord_value(f.readline(), base)
                    if value > threshold:
                        vertices += 1
                        # print(f"coord: {coord}  value: {value}")
                        ff.write(f"{coord[0]} {coord[1]} {coord[2]} {value}\n")

                # print(f"block  {block} end")
                block += 1
                continue
            elif line == "":
                break
            else:
                continue
        ff.close()
    exec_time = time.time() - start_time

def exec_blocks3(f, prefix, file_path, threshold = 0.0):
    start_time = time.time()
    data = {}
    block = 0
    vertices = 0
    while True:
        line = f.readline()

        if line == "      [" + str(block) + "]: {\n":
            # print(f"find block {block} : ")

            # 解析base coordinate
            base = get_base_coordinate(f.readline())
            # print(f"base: {base}")
            for j in range(64):
                coord, value = get_coord_value(f.readline(), base)
                if value > threshold:
                    vertices += 1
                    # ff.write(f"{coord[0]} {coord[1]} {coord[2]} {value}\n")
                    data[coord] = [value, None]

            block += 1
            continue

        elif "      coord: " in line:
            square_brackets = line.split(":")[1]
            x, y, z = value_from_square_brackets(square_brackets)
            next_line = f.readline()
            parts = next_line.split(":")
            if parts[0].strip() != "f":
                continue
            square_brackets = parts[1]
            f_x, f_y, f_z = float_from_square_brackets(square_brackets)
            if data[(x, y, z)] is not None:
                data_item = list(data[(x, y, z)])
                print("found exist data")
                data_item[1] = (f_x, f_y, f_z)
                data[(x, y, z)] = data_item
            else:
                print("null data")
                return
        elif line == "":
            break
        else:
            continue

    with open(file_path, 'w', encoding='utf-8') as ff:
        ff.write(prefix)
        ff.close()
    with open(file_path, 'a', encoding='utf-8') as ff:
        for coord in data:
            print(f"coord: {coord}")
            values = list(data[coord])
            density = values[0]
            force = values[1]
            if force is None:
                force = (0,0,0)
            ff.write(f"{coord[0]} {coord[1]} {coord[2]} {density} {force[0]} {force[1]} {force[2]}\n")
        ff.close()


    exec_time = time.time() - start_time



def count_valid_points_fast2(ff):
    block = 0
    while True:
        line = ff.readline()
        if line == "      [" + str(block) + "]: {\n":
            block += 1
            continue
        elif line == "":
            break
    return block * 64

if __name__ == "__main__":
    with_fem = True
    input_path = "./00200.txt"
    output_path = "00200.ply"

    with open(input_path, 'r') as f:
        # lines = f.readlines()
        valid_points = count_valid_points_fast2(f)
        f.close()
        print(valid_points)

    if with_fem:
        prefix = f"ply\n" \
                 f"format ascii 1.0\n" \
                 f"comment author: Jeremy\n" \
                 f"comment object: Topo\n" \
                 f"element vertex {valid_points}\n" \
                 f"property float x\n" \
                 f"property float y\n" \
                 f"property float z\n" \
                 f"property float density\n" \
                 f"property float f_x\n" \
                 f"property float f_y\n"\
                 f"property float f_z\n" \
                 f"end_header\n"
    else:
        prefix = f"ply\n" \
                 f"format ascii 1.0\n" \
                 f"comment author: Jeremy\n" \
                 f"comment object: Topo\n" \
                 f"element vertex {valid_points}\n" \
                 f"property float x\n" \
                 f"property float y\n" \
                 f"property float z\n" \
                 f"property float density\n" \
                 f"end_header\n"
    with open(input_path, 'r') as f:
        if with_fem:
            exec_blocks3(f, prefix, output_path, threshold=0)
        else:
            exec_blocks2(f, prefix, output_path, threshold=0)
        f.close()
