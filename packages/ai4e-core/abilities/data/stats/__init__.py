"""统计量读取与具名数组流累计。"""

from .fit import fit_statistics
from .load import load_statistics, write_statistics
from .moments import accumulate_moments

__all__ = ["accumulate_moments", "fit_statistics", "load_statistics", "write_statistics"]
