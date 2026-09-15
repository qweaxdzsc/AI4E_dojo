"""VTK内核对象的进程内有界缓存原语。"""

from collections import OrderedDict


class KernelCache[ValueT]:
    """不理解业务键含义的简单LRU缓存。"""

    def __init__(self, capacity: int = 16) -> None:
        """创建固定容量缓存，容量必须大于零。"""

        if capacity <= 0:
            raise ValueError("缓存容量必须大于零")
        self._capacity = capacity
        self._values: OrderedDict[str, ValueT] = OrderedDict()

    def get(self, key: str) -> ValueT | None:
        """读取并提升缓存项；不存在时返回None。"""

        value = self._values.get(key)
        if value is not None:
            self._values.move_to_end(key)
        return value

    def put(self, key: str, value: ValueT) -> None:
        """写入缓存并淘汰最久未使用项。"""

        self._values[key] = value
        self._values.move_to_end(key)
        while len(self._values) > self._capacity:
            self._values.popitem(last=False)

    def clear(self) -> None:
        """释放全部缓存引用，供会话结束或内存治理使用。"""

        self._values.clear()


def geometry_signature(mesh) -> str:
    """按实际几何和拓扑判定复用；点数相同不足以证明拓扑未变化。"""
    import hashlib

    from vtk.util.numpy_support import vtk_to_numpy

    digest = hashlib.sha256(mesh.GetClassName().encode())
    digest.update(
        str((mesh.GetNumberOfPoints(), mesh.GetNumberOfCells(), mesh.GetBounds())).encode()
    )
    if mesh.IsA("vtkImageData"):
        digest.update(
            str(
                (
                    mesh.GetExtent(),
                    mesh.GetOrigin(),
                    mesh.GetSpacing(),
                    tuple(
                        mesh.GetDirectionMatrix().GetElement(i, j)
                        for i in range(3)
                        for j in range(3)
                    ),
                )
            ).encode()
        )
    else:
        if hasattr(mesh, "GetPoints") and mesh.GetPoints():
            digest.update(vtk_to_numpy(mesh.GetPoints().GetData()).tobytes())
        for name in ("GetCells", "GetVerts", "GetLines", "GetPolys", "GetStrips"):
            if hasattr(mesh, name):
                cells = getattr(mesh, name)()
                if cells:
                    digest.update(vtk_to_numpy(cells.GetOffsetsArray()).tobytes())
                    digest.update(vtk_to_numpy(cells.GetConnectivityArray()).tobytes())
        if hasattr(mesh, "GetCellTypesArray") and mesh.GetCellTypesArray():
            digest.update(vtk_to_numpy(mesh.GetCellTypesArray()).tobytes())
    return digest.hexdigest()


def reuse_geometry(mesh, previous):
    """同几何共享结构与 VTK 对象身份，场数组仍使用当前真实帧。"""
    signature = geometry_signature(mesh)
    if previous and previous[0] == signature:
        # CopyStructure 对某些 VTK 数据集会清空属性；当前帧数组必须独立保存。
        attributes = []
        for getter in ("GetPointData", "GetCellData", "GetFieldData"):
            current = getattr(mesh, getter)()
            saved = current.NewInstance()
            saved.ShallowCopy(current)
            attributes.append((getter, saved))
        mesh.CopyStructure(previous[1])
        for getter, saved in attributes:
            getattr(mesh, getter)().ShallowCopy(saved)
    return signature, mesh
