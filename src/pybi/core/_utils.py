from dataclasses import dataclass
from typing import Any

from instaui import ui
from ._mixins import SqlQueryProtocol
from .page_state import PageState


@dataclass
class FilterableResult:
    event_inputs: list[Any]
    event_output: dict


@dataclass
class SourceableResult:
    inputs: list[Any]


def filterable(query: SqlQueryProtocol):
    page_state = PageState.get()
    central = page_state.central
    sql_store = page_state.sql_store
    dataset = query.dataset
    sid = query.sql_id

    filter_target_id = sql_store.get_dependency_of_first_data_view(sid)
    deps_of_data_view_ids = sql_store.get_all_dependencies_of(
        filter_target_id, type="data_view"
    )

    return FilterableResult(
        event_inputs=[
            central.component_ref,
            central.filters_state,
            filter_target_id,
            deps_of_data_view_ids,
        ],
        event_output=central.filters_state,
    ), dataset


def sourceable(query: SqlQueryProtocol):
    page_state = PageState.get()
    central = page_state.central
    sql_store = page_state.sql_store
    dataset = query.dataset
    sid = query.sql_id

    all_deps_of_data_view_ids = set(
        sql_store.get_all_dependencies_of(sid, type="data_view")
    )
    # 还需要排除最近一个 data_view 的依赖，因为它会导致自身的重新计算
    all_deps_of_data_view_ids.remove(sql_store.get_dependency_of_first_data_view(sid))

    filter_signal = central.signal(all_deps_of_data_view_ids)

    return SourceableResult(
        [central.sql_table, ui.slient(central.filters_state), *filter_signal]
    ), dataset
