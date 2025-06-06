from __future__ import annotations
import typing
from instaui import ui
from pybi.link_sql.data_set_store import get_data_set
from pybi.link_sql.data_view_store import get_store as get_view_store, Store
from pybi.link_sql.filters import get_related_filters
from pybi.link_sql import sql_stem
from dataclasses import dataclass


def create_source(
    sql: str,
    *,
    dataset_id: typing.Optional[int] = None,
    exclude_filter_view_name: typing.Optional[str] = None,
    exclude_filter_query_key: typing.Optional[str] = None,
) -> SourceInfo:
    query_name = sql_stem.gen_query_name()
    store = get_view_store()
    store.store_query(query_name, sql)

    dataset_id = _get_dataset_id(store, sql, dataset_id)

    filters = get_related_filters(
        query_name,
        target_view=exclude_filter_view_name,
        query_key=exclude_filter_query_key,
    )

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
        filters: typing.Dict,
        sql_map: typing.Dict[str, str],
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
        self._source._mark_used()
        return self._source

    def flat_values(self):
        self._source._mark_used()
        return ui.js_computed(
            inputs=[self.source],
            code=r"""source=>{
    const {values} = source
    return values.flat()                      
}""",
        )


def _get_dataset_id(
    view_store: Store, sql: str, dataset_id: typing.Optional[int] = None
) -> int:
    if dataset_id is not None:
        return dataset_id

    any_view_name = sql_stem.extract_any_view_name(sql, view_store.server_sql_map)
    return view_store.get_view(any_view_name).dataset_id
