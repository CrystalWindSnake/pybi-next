from typing import Any, Union
from typing_extensions import Unpack
from instaui import ui
from instaui_tdesign import td
from instaui_tdesign.components.table import TPrimaryTableProps
from pybi.core.data_view import DataView
from pybi.core.data_field import DataFieldSet
from pybi.core import _utils
from pybi.core.sql_store import get_sql

_DEFAULT_PROPS = {}


def table(
    data: Union[DataView, DataFieldSet],
    **kwargs: Unpack[TPrimaryTableProps],
):
    real_data = data.build_query() if isinstance(data, DataFieldSet) else data

    cp_id = _utils.gen_component_id()
    sid = real_data.sql_id
    real_data.bind_component(cp_id)

    sourceable_result, dataset = _utils.sourceable(real_data, cp_id)

    @ui.computed(
        inputs=[
            cp_id,
            sid,
            *sourceable_result.inputs,
        ]
    )
    def table_data(cp_id: str, sql_id: str, sql_table: dict, filters: dict, *_: Any):
        sql, params = get_sql(
            sql_id, sql_table=sql_table, filters=filters, exclude_components=[cp_id]
        )

        result = dataset.query(sql, params)
        data = [
            {col: val for col, val in zip(result["columns"], row)}
            for row in result["values"]
        ]

        return {"data": data, "columns": result["columns"]}

    props = {**_DEFAULT_PROPS, **kwargs}

    return td.table(table_data["data"], **props)
