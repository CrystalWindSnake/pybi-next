__all__ = [
    "__version__",
    "data_view",
    "query",
    "label",
    "duckdb",
    "column",
    "row",
    "grid",
    "select",
    "table",
    "input",
    "radio",
    "echarts",
]

from .version import __version__
from instaui.ui import column, row, label, grid
from .link_sql import duckdb
from .components.radio import radio
from .components.select import select
from .components.table import table
from .components.input import input
from .components.echarts import echarts
from .link_sql.data_view import data_view
from .link_sql.query import query


from . import _setup  # noqa: F401
