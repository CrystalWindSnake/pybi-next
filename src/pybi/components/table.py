from typing_extensions import Unpack
from instaui import arco, ui
from instaui.arco import component_types

from pybi.link_sql._mixin import DataTableMixin
from pybi.link_sql import _server_query


def table(
    query: DataTableMixin,
    **kwargs: Unpack[component_types.TTable],
):
    query_name = query.get_query_name()
    dataset_id = query.dataset_id

    source_from_server = _server_query.create_source(query_name, dataset_id=dataset_id)

    info = ui.js_computed(
        inputs=[source_from_server.source],
        code=r"""source=>{
        const columns = source.columns;
        const values = source.values;
        const real_cols = columns.map(col => ({title: col, dataIndex: col, ellipsis: true, tooltip: true}));
        const real_values = values.map(row => Object.fromEntries(row.map((value,index) => [columns[index], value])));
        return {columns: real_cols, data: real_values};                     
}""",
    )

    args = {**kwargs, "columns": info["columns"], "data": info["data"]}

    return arco.table(**args)
