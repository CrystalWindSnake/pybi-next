from __future__ import annotations
import typing
from instaui import ui
from pybi.link_sql.data_set_store import get_data_set
from pybi.link_sql.data_view_store import get_store as get_view_store, Store
from pybi.link_sql import _types, sql_stem
from dataclasses import dataclass


def create_source(
    query_name: str,
    *,
    dataset_id: typing.Optional[int] = None,
    exclude_filter: typing.Optional[_types.TExcludeFilter] = None,
) -> SourceInfo:
    store = get_view_store()

    dataset_id = _get_dataset_id(store, query_name, dataset_id)

    filters = store.build_related_filters(query_name, exclude_filter=exclude_filter)

    info = {
        "main_query": query_name,
        "dataset_id": dataset_id,
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
        filters: typing.Any,
        sql_map: typing.Dict[str, typing.Any],
        sql_orders: typing.Dict[str, int],
    ):
        sql, params = sql_stem.build_sql(
            main_query_name=info["main_query"],
            filters=filters,
            sql_map=sql_map,
            sql_orders=sql_orders,
        )

        rest = get_data_set(info["dataset_id"]).query(sql, params)
        return rest

    return SourceInfo(source_from_server, query_name)


@dataclass(frozen=True)
class SourceInfo:
    _source: ui.TComputed
    query_name: str

    @property
    def source(self):
        return self._source

    def flat_values(self):
        return ui.js_computed(
            inputs=[self.source],
            code=r"""source=>{
    const {values} = source
    return values.flat()                      
}""",
        )

    def values(self):
        return ui.js_computed(
            inputs=[self.source],
            code=r"""source=>{
    return source.values
}""",
        )

    def columns(self):
        return ui.js_computed(
            inputs=[self.source],
            code=r"""source=>{
    return source.columns
}""",
        )


def _get_dataset_id(
    view_store: Store, query_name: str, dataset_id: typing.Optional[int] = None
) -> int:
    if dataset_id is not None:
        return dataset_id

    any_view_name = sql_stem.extract_any_view_name(
        view_store.get_sql(query_name), view_store.server_sql_map
    )
    return view_store.get_view_dataset_id(any_view_name)


@dataclass(frozen=True)
class ChartSourceInfo:
    _source: ui.TComputed
    query_index: int

    @property
    def source(self):
        return self._source

    def flat_values(self):
        return ui.js_computed(
            inputs=[self.source],
            code=r"""source=>{
    const {values} = source
    return values.flat()                      
}""",
        )


def create_chart_source(
    sqls: typing.Iterable[str],
    *,
    current_query_index=0,
    dataset_id: typing.Optional[int] = None,
    exclude_filter: typing.Optional[_types.TExcludeFilter] = None,
) -> ChartSourceInfo:
    info, query_index = _create_chart_infos(
        sqls,
        current_query_index,
        dataset_id,
        exclude_filter,
    )

    store = get_view_store()

    @ui.computed(
        inputs=[
            info,
            query_index,
            store.sql_map,
            store.sql_orders,
        ]
    )
    def source_from_server(
        info: typing.Dict,
        query_index: int,
        sql_map: typing.Dict[str, _types.TSqlMapValue],
        sql_orders: typing.Dict[str, int],
    ):
        main_query_name = info["query"]
        filters = info["filters"]
        dataset_id = info["dataset_id"]

        sql, params = sql_stem.build_sql(
            main_query_name=main_query_name,
            filters=filters,
            sql_map=sql_map,
            sql_orders=sql_orders,
        )

        rest = get_data_set(dataset_id).query(sql, params)
        return rest

    return ChartSourceInfo(source_from_server, query_index)


def _create_chart_infos(
    sqls: typing.Iterable[str],
    current_query_index: int,
    dataset_id: typing.Optional[int] = None,
    exclude_filter: typing.Optional[_types.TExcludeFilter] = None,
):
    current_query_index_state = ui.state(current_query_index)
    query_names = []
    filters_list = []
    dataset_id_list = []

    for sql in sqls:
        store = get_view_store()
        query_name = store.gen_query(sql)

        dataset_id = _get_dataset_id(store, query_name, dataset_id)

        filters = store.build_related_filters(query_name, exclude_filter=exclude_filter)

        query_names.append(query_name)
        filters_list.append(filters)
        dataset_id_list.append(dataset_id)

    filters_array = ui.js_computed(
        inputs=filters_list, code=r"""(...filters_list)=>filters_list"""
    )

    chart_info = ui.js_computed(
        inputs=[current_query_index_state, query_names, filters_array, dataset_id_list],
        code=r"""(index,query_names, filters_array, dataset_id_list)=>{
    return {
        query:query_names[index],
        filters:filters_array[index],
        dataset_id:dataset_id_list[index]
    }                 
}""",
        deep_compare_on_input=True,
    )

    return chart_info, current_query_index_state
