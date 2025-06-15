from typing import Optional
from pybi.link_sql.data_view_store import get_store
from pybi.link_sql import sql_stem
from instaui import ui


def get_related_filters(
    source_name: str,
    *,
    target_view: Optional[str] = None,
    query_key: Optional[str] = None,
):
    store = get_store()

    # orders = sql_stem.get_sql_execution_order(store._sql_map)
    # source_level = orders[source_name]

    views = sql_stem.get_upstream_dataview_names(source_name, store._sql_map)
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


def add_filter_js_fn():
    """

    Example:
    .. code-block:: python

        dv1_filters = dev.query_map().get_filters(dv1)

        add_f1 = ui.js_event(
            inputs=[dv1_filters, pybi.add_filter_js_fn()],
            outputs=[dv1_filters],
            code=r''' (filters, add_filter)=>{
        return add_filter(filters, 'f1', {expr: 'Name = ?', value: 'foo1'})
    }''',
        )
    """
    return get_store()._add_filters_js_handler


def remove_filter_js_fn():
    """

    Example:
    .. code-block:: python

        dv1_filters = dev.query_map().get_filters(dv1)

        add_f1 = ui.js_event(
            inputs=[dv1_filters, pybi.remove_filter_js_fn()],
            outputs=[dv1_filters],
            code=r''' (filters, remove_filter)=>{
        return remove_filter(filters, 'f1')
    }''',
        )
    """

    return get_store()._remove_filters_js_handler
