
import numpy as np
import open3d as o3d
from typing import Tuple

"""
该文件为使用open3d库打开ply文件的尝试，已被弃用
"""

def read_ply_file(file_path: str) -> Tuple:
    # Read .ply file using open3d library
    pcd = o3d.io.read_point_cloud(file_path)
    o3d.geometry.PointCloud.points.fget()
    # Extract point position and density data
    points = np.asarray(pcd.points)
    densities = np.asarray(pcd.colors)[:, 0] * 255.0

    return points, densities



def create_polygon_mesh(points: np.ndarray, densities: np.ndarray) -> o3d.geometry.TriangleMesh:
    # Filter out points with density greater than 0.5
    dense_points = points[densities > 0.5]
    # Create a KDTree for fast nearest neighbor search
    tree = o3d.geometry.KDTreeFlann(dense_points)

    # Create a list to store polygon vertices
    vertices = []

    # Create a list to store polygon faces
    faces = []

    # Iterate through each dense point
    for i in range(dense_points.shape[0]):
        # Find the 6 nearest neighbors of the current point
        [k, idx, _] = tree.search_knn_vector_3d(dense_points[i], 6)

        # Add the current point to the list of vertices
        vertices.append(dense_points[i])

        # Loop over each neighbor and add a face to the list of faces
        for j in range(1, k):
            faces.append([i, idx[j], idx[j - 1]])

    # Create a polygon mesh from the vertices and faces
    mesh = o3d.geometry.TriangleMesh(vertices,faces)
    return mesh



if __name__ == "__main__":
    print("Load a ply point cloud, print it, and render it")
    # ply_point_cloud = o3d.data.PLYPointCloud()
    path = r"00200.ply"
    pcd = o3d.io.read_point_cloud(path)
    # print(pcd)
    points = np.asarray(pcd.points)
    print("max")
    x_max = np.max(points[:,0])
    y_max = np.max(points[:, 1])
    z_max = np.max(points[:,2])

    o3d.visualization.draw_geometries([pcd],
                                      zoom=0.9,
                                      front=[0, 0, 1],
                                      lookat=[x_max/2, y_max/2, z_max/2],
                                      up=[0, 1, 0])
