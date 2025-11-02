from dataclasses import dataclass
from typing import Any

from instaui import ui

from pybi.core._types import TComponentId, TDataViewId
from ._mixins import SqlQueryProtocol
from .page_state import PageState


@dataclass
class FilterableResult:
    event_inputs: list[Any]
    event_output: dict


@dataclass
class SourceableResult:
    inputs: list[Any]


def gen_component_id():
    return PageState.get().component_store.gen_component_id()


def filterable(query: SqlQueryProtocol, *, filter_target_id: TDataViewId):
    page_state = PageState.get()
    central = page_state.central
    dataset = query.dataset

    return FilterableResult(
        event_inputs=[
            central.component_ref,
            central.filters_state,
            filter_target_id,
        ],
        event_output=central.filters_state,
    ), dataset


def sourceable(query: SqlQueryProtocol, cp_id: TComponentId):
    page_state = PageState.get()
    central = page_state.central
    dataset = query.dataset

    central.register_signal(cp_id)
    filter_signal = central.signal(cp_id)

    return SourceableResult(
        [central.sql_table, ui.slient(central.filters_state), filter_signal]
    ), dataset
