import typing
from instaui import ui

from pybi.link_sql.data_set_store import get_data_set
from pybi.link_sql.data_view import get_store as get_view_store
from pybi.link_sql.filters import get_related_filters
from pybi.link_sql import sql_stem


def query(sql: str):
    store = get_view_store()
    query_name = sql_stem.gen_query_name()
    store.store_query(query_name, sql)

    filters = get_related_filters(query_name)

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
