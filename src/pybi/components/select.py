import typing
from typing_extensions import Unpack
from instaui import arco, ui
from instaui.arco import component_types
from pybi.link_sql.data_view_store import get_store as get_view_store
from pybi.link_sql._mixin import DataColumnMixin
from pybi.link_sql import _server_query, _types

_DEFAULT_PROPS = {
    "allow-clear": True,
}


def select(
    options: DataColumnMixin,
    value: typing.Optional[ui.TMaybeRef[typing.Union[str, int]]] = None,
    **kwargs: Unpack[component_types.TSelect],
):
    source_type = options.get_source_type()
    source_name = options.source_name
    field = options.field
    store = get_view_store()

    exclude_filter: typing.Optional[_types.TExcludeFilter] = None
    if source_type == "view":
        exclude_filter = {
            "view_name": source_name,
            "query_key": f"{field}-{store.gen_field_query_id(field)}",
        }

    query_name = store.gen_query(
        f"SELECT DISTINCT {field} FROM {source_name} ORDER BY {field} ASC"
    )

    source_from_server = _server_query.create_source(
        query_name,
        exclude_filter=exclude_filter,
    ).flat_values()

    props = {**_DEFAULT_PROPS, "placeholder": field, **kwargs}

    element = arco.select(options=source_from_server, value=value, **props)  # type: ignore

    if source_type == "view":
        assert exclude_filter is not None

        on_change = ui.js_event(
            inputs=[
                ui.event_context.e(),
                source_name,
                field,
                exclude_filter["query_key"],
                store._add_filters_js_handler,
                store._remove_filters_js_handler,
            ],
            outputs=[store._element_ref],
            code=r"""(value,view_name,field,query_key,addFilter,removeFilter) => {

    if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)){
        return removeFilter(view_name, query_key)
    }

    const realValue = Array.isArray(value)? value : [value];
    return addFilter(view_name, query_key, {expr: `${field} in ?`,value:realValue})
    }""",
        )
        element.on_change(on_change)

    return element
