from typing import Optional, Sequence, Union
from itertools import chain
from instaui import ui
from pybi.link_sql import sql_stem
from pybi.link_sql.data_view_store import get_store as get_view_store
from pybi.link_sql import _types


def get_related_filters(
    source_names: Union[str, Sequence[str]],
    *,
    source_index: int = 0,
    exclude_infos: Optional[Sequence[_types.TExcludeFilter]] = None,
):
    source_names = [source_names] if isinstance(source_names, str) else source_names

    # [[f1,f2],[f3,f4],[f5,f6]]
    filters = list(chain.from_iterable([_get_filters(name) for name in source_names]))

    source_count = len(source_names)
    agg_filters = ui.js_computed(
        inputs=[source_index, source_count, *filters],
        code=r"""(index,source_count , ...filters)=>{  
              
    function chunkArray(arr, count) {
        let result = [];
        for (let i = 0; i < arr.length; i += count) {
            let chunk = arr.slice(i, i + count);
            result.push(chunk);
        }
        return result;
    }
                                  
    const grouped_filters = source_count===1? [filters] : chunkArray(filters, source_count)                           
    return grouped_filters[index]                                           
}""",
        deep_compare_on_input=True,
    )

    return agg_filters


def _get_filters(source_name: str):
    store = get_view_store()
    sql_map = store.server_sql_map

    stack = [source_name]
    view_names = set()
    while stack:
        name = stack.pop()
        if sql_stem.get_source_type(name) == "view":
            view_names.add(name)

        sql = sql_map[name]["sql"]
        stack.extend(sql_stem.iter_extract_names(sql))

    return [store.sql_map[name]["filters"] for name in view_names]
