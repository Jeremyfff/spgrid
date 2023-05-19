import os.path
import time
import numpy as np
import datatable as dt
from scipy.spatial import cKDTree
from tqdm import tqdm
import random


class Face:
    def __init__(self, index, vertices, group=None):
        self.index = index  # 第几个
        self.normal = input_normals[index]  # 法线
        self.vertices = set(vertices)  # 点的序号
        self.neighbours = set()  # 邻居面
        self.group = group  # 第几组
        self.center = self.get_center() # 中心点

    def add_neighbour(self, neighbour):
        self.neighbours.add(neighbour)

    def get_center(self):
        p = list(self.vertices)
        pts = np.array([input_vertices[int(p[i])] for i in range(3)])
        return np.mean(pts, axis=0)


def dot(a, b):
    return sum([a[i] * b[i] for i in range(len(b))])

file_path = r"D:\M.Arch\2023Spr\DesignClass_ComputationalDesignandHigh-performance3DPrintingConstruction\final\tmp"
input_vertices = dt.fread(os.path.join(file_path, "vertices.csv")).to_numpy()
input_normals = dt.fread(os.path.join(file_path, "normals.csv")).to_numpy()
input_faces = dt.fread(os.path.join(file_path, "faces.csv")).to_numpy()

all_faces = []
face_points = []

for i in tqdm(range(len(input_normals))):
    normal = input_normals[i]
    f = input_faces[i]
    vertices = {int(f[0]), int(f[1]), int(f[2])}
    face = Face(i, vertices)
    all_faces.append(face)
    face_points.append(face.center)

print("creating KDTree")
face_points = np.array(face_points)
kdtree = cKDTree(face_points)

c = "5"
c_float = 5
while c != "":
    for i in range(10):
        print(len(kdtree.query_ball_point(face_points[random.randint(0,len(face_points))], r=float(c), p=2)))
    c_float = float(c)
    c = input(f"current c = {c}, change value or confirm(enter)? ")

print("finding neighbours...")
start = time.time()
# find neighbours
for i in tqdm(range(len(all_faces))):
    face1 = all_faces[i]
    # Query kdtree to find nearby faces
    neighbors_indices = kdtree.query_ball_point(face_points[i], r=c_float, p=2)
    neighbors_indices.remove(i)  # Remove the current face from the neighbors
    for idx in neighbors_indices:
        face2 = all_faces[idx]
        if len(face1.vertices.intersection(face2.vertices)) >= 2:
            face1.add_neighbour(face2)
            face2.add_neighbour(face1)


end1 = time.time()
print(f"code1 finished in {(end1 - start)*1000}ms")
# 校验
for i in range(10):
    # print(len(kdtree.query_ball_point(face_points[random.randint(0, len(face_points))], r=float(c), p=2)))
    print(len(all_faces[random.randint(0, len(all_faces))].neighbours))

face_indexes = {}
seen = {}
face_in_queue = []
current_group = 0

all_faces_suffle = []
for face in all_faces:
    all_faces_suffle.append(face)
random.shuffle(all_faces_suffle)

print("splitting mesh...")
for i in tqdm(range(len(all_faces_suffle))):
    face = all_faces_suffle[i]
    if face in seen:
        continue
    face_indexes[current_group] = []
    face_in_queue.append(face)
    max_search_round = 100

    while face_in_queue and max_search_round:
        for face1 in face_in_queue:
            face_in_queue.remove(face1)
            if face1 in seen:
                continue
            if dot(face1.normal, face.normal) < 0.2:
                continue
            face_indexes[current_group].append(face1)
            face1.group = current_group
            seen[face1] = 1
            for face2 in face1.neighbours:
                face_in_queue.append(face2)
        max_search_round -= 1
    current_group += 1

output_group = []
for face in all_faces:
    output_group.append(face.group)

end2 = time.time()
print(f"code2 finished in {(end2 - end1)*1000}ms")

with open(os.path.join(file_path,"group.csv"), "w") as f:
    for group in output_group:
        f.write(f"{group}\n")
f.close()


group = 0
while True:
    count = output_group.count(group)
    if count == 0:
        break
    if count == 1:
        group += 1
        continue
    print(f"group[{group}] count:{count}")
    group += 1
