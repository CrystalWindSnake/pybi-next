from typing_extensions import Unpack
from instaui import arco, ui
from instaui.arco import component_types

from pybi.link_sql.data_view_store import get_store as get_view_store
from pybi.link_sql._mixin import DataColumnMixin
from pybi.link_sql import _server_query

_DEFAULT_PROPS = {}


def radio(
    options: DataColumnMixin,
    **kwargs: Unpack[component_types.TRadio],
):
    source_type = options.get_source_type()
    source_name = options.source_name
    field = options.field

    exclude_filter_view_name = None
    exclude_filter_query_key = None
    if source_type == "view":
        exclude_filter_view_name = source_name
        exclude_filter_query_key = (
            f"{field}-{get_view_store().gen_field_query_id(field)}"
        )

    source_from_server = _server_query.create_source(
        f"SELECT DISTINCT {field} FROM {source_name}",
        exclude_filter_view_name=exclude_filter_view_name,
        exclude_filter_query_key=exclude_filter_query_key,
    ).flat_values()

    props = {**_DEFAULT_PROPS, **kwargs, "options": source_from_server}

    element = arco.radio_group(**props)

    if source_type == "view":
        view_store = get_view_store()

        on_change = ui.js_event(
            inputs=[
                ui.event_context.e(),
                view_store.get_filters(source_name),
                exclude_filter_query_key,
                field,
            ],
            outputs=[view_store.get_filters(source_name)],
            code=r"""(value,filters,query_key,field) => {

    if (value === null || value === undefined || value === '' ){
        const {[query_key]:_, ...rest} = filters
        return rest    
    }

    return {...filters, [query_key]: {expr: `${field} in ?`,value}}
    }""",
        )
        element.on_change(on_change)
