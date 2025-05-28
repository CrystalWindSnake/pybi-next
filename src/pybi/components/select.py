import typing
from typing_extensions import Unpack
from instaui import arco, ui
from instaui.arco import component_types

from pybi.link_sql.data_set_store import get_data_set
from pybi.link_sql.data_view import get_store as get_view_store
from pybi.link_sql.filters import get_related_filters
from pybi.link_sql import sql_stem
from pybi.link_sql._mixin import DataColumnMixin

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

    # 获取数据
    store = get_view_store()
    query = f"SELECT DISTINCT {field} FROM {source_name}"
    query_name = sql_stem.gen_query_name()
    store.store_query(query_name, query)
    query_id = store.gen_field_query_id(field)
    query_key = f"{field}-{query_id}"

    filters = get_related_filters(
        source_name,
        target_view=source_name,
        query_key=query_key,
    )

    info = {
        "main_query": query_name,
        "dataset_id": store.get_view(source_name).dataset_id,
    }

    @ui.computed(
        inputs=[
            info,
            filters,
            store.sql_map,
            store.sql_orders,
        ]
    )
    def source_from_server(
        info: typing.Dict,
        filters: typing.Dict,
        sql_map: typing.Dict[str, str],
        sql_orders: typing.List[str],
    ):
        sql, params = sql_stem.build_sql(
            main_query_name=info["main_query"],
            filters=filters,
            sql_map=sql_map,
            sql_orders=sql_orders,
        )

        rest = get_data_set(info["dataset_id"]).query(sql, params).flat_values()
        print(f"{sql=}, {params=}, {rest=}")
        return rest

    props = {**_DEFAULT_PROPS, "placeholder": field, **kwargs}

    element = arco.select(options=source_from_server, value=value, **props)  # type: ignore

    if source_type == "view":
        on_change = ui.js_event(
            inputs=[
                ui.event_context.e(),
                store.get_filters(source_name),
                query_key,
                field,
            ],
            outputs=[store.get_filters(source_name)],
            code=r"""(value,filters,query_key,field) => {

    if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)){
        const {[query_key]:_, ...rest} = filters
        return rest    
    }

    const realValue = Array.isArray(value)? value : [value];

    return {...filters, [query_key]: {expr: `${field} in ?`,value:realValue}}
    }""",
        )
        element.on_change(on_change)

    return element

    # return arco.select(options=source_from_server, value=value, **props).on_change(
    #     on_change
    # )  # type: ignore

    # data_view = options.get_data_view()
    # field = options.field
    # query_id = DataViewStore.get().gen_field_query_id(field)
    # query_key = f"{field}-{query_id}"
    # exclude_info = ExcludeFilterInfo(
    #     data_view_name=data_view.str_name, query_key=query_key
    # )

    # main_query_sql = f"SELECT DISTINCT {field} FROM {data_view} ORDER BY {field} ASC"
    # source = query(
    #     main_query_sql,
    #     dataset=data_set_store.try_get_data_set(data_view._dataset_id),
    #     exclude_info=exclude_info,
    # ).flat_values()


#     element_ref = options.get_element_ref()

#     props = {**_DEFAULT_PROPS, "placeholder": field, **kwargs}

#     on_change = ui.js_event(
#         inputs=[ui.event_context.e(), field, query_id],
#         outputs=[element_ref],
#         code=r"""(value,field,query_id) => {

# if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)){
#     return {method:'removeFilter', args:[{field,query_id}]};
# }

# const realValue = Array.isArray(value)? value : [value];
# return {method: 'addFilter', args:[{field, expr: `${field} in ?`,value,query_id}]};
# }""",
#     )

#     return arco.select(options=source_from_server, value=value, **props).on_change(
#         on_change
#     )  # type: ignore
