import typing
from typing_extensions import Unpack
from instaui import arco, ui
from instaui.arco import component_types

from pybi.link_sql import data_set_store
from pybi.link_sql._mixin import DataColumnMixin
# from pybi.link_sql.data_view_store import DataViewStore
# from pybi.link_sql.query import query

_DEFAULT_PROPS = {}


def radio(
    options: DataColumnMixin,
    **kwargs: Unpack[component_types.TRadio],
):
    data_view = options.get_data_view()
    field = options.field
    query_id = DataViewStore.get().gen_field_query_id(field)
    query_key = f"{data_view.str_name}-{field}-{query_id}"

    main_query_sql = (
        f"SELECT DISTINCT {field} FROM ({data_view.sql_str}) ORDER BY {field} ASC"
    )
    source = query(
        main_query_sql,
        dataset=data_set_store.try_get_data_set(data_view._dataset_id),
        exclude_query_key=query_key,
        exclude_view_name=data_view.str_name,
    ).flat_values()

    element_ref = options.get_element_ref()

    props = {**_DEFAULT_PROPS, **kwargs}

    on_change = ui.js_event(
        inputs=[ui.event_context.e(), field, query_id],
        outputs=[element_ref],
        code=r"""(value,field,query_id) => {
if (value) {
return {method: 'addFilter', args:[{field, expr: `${field}= ?`,value,query_id}]};
}

return {method:'removeFilter', args:[{field,query_id}]};
        }""",
    )

    with arco.radio_group(**props) as group:
        with ui.vfor(source) as item:
            with arco.radio(item):
                ui.content(item)

    return group.on_change(on_change)  # type: ignore
