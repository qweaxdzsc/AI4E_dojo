"""首期能力边界。"""

from fastapi import APIRouter

from .aero_cfd import OUTPUTS, SOURCES

router = APIRouter()


@router.get("/capabilities")
def capabilities():
    """描述首期可表达的案例能力和限制。"""
    return {
        "stages": ["rawprep"],
        "parallelism": 1,
        "sources": SOURCES,
        "outputs": OUTPUTS,
        "formats": ["vtk", "vtp", "vtu", "vtkhdf", "npy", "pt", "txt", "csv", "json", "yaml"],
        "unsupported": ["batch", "arbitrary_tensor_bundle", "output_rename", "remote_execution"],
    }
