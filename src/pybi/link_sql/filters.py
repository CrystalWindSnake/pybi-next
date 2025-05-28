from typing import Optional
from pybi.link_sql.data_view import get_store
from pybi.link_sql import sql_stem
from instaui import ui


def get_related_filters(
    source_name: str,
    *,
    target_view: Optional[str] = None,
    query_key: Optional[str] = None,
):
    store = get_store()

    orders = sql_stem.get_sql_execution_order(store._sql_map)
    index = orders.index(source_name)
    orders = orders[: index + 1]

    views = [name for name in orders if sql_stem.get_source_type(name) == "view"]
    filters = [store.get_filters(name) for name in views]

    aggregate_filter = ui.js_computed(
        inputs=[views, target_view, query_key, *filters],
        code=r"""(names,target_view,query_key, ...filters)=> {
        const filterMap = names.map((name,i) => {
            const filter = filters[i]

            if (target_view && name === target_view){
                const {[query_key]: _,...filter_without_query_key} = filter
                return [name, filter_without_query_key]
            }

            return [name, filter]
        })

        return Object.fromEntries(filterMap)
}""",
        deep_compare_on_input=True,
    )

    return aggregate_filter
