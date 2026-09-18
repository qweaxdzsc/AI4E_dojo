"""用户连接代码：转换发生在使用处，不修改两端组件。"""


def mesh_to_points(mesh):
    """下一步需要坐标序列，故显式取出顶点。"""
    return mesh.vertices
