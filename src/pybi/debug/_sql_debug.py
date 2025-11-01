from __future__ import annotations
from instaui import ui
from instaui_tdesign import td
from pybi.core.page_state import PageState


def view_info():
    page_state = PageState.get()
    central = page_state.central

    @ui.computed(inputs=[central.sql_table, central.filters_state])
    def data(sql_table: dict[str, dict], filters: dict[str, dict]):
        return [
            {
                "sql_id": sql_id,
                "template": info["template"],
                "type": info["type"],
                "references": info.get("references", []),
                "components": info.get("components", []),
                "filters": repr(filters.get(sql_id, {})),
            }
            for sql_id, info in sql_table.items()
        ]

    with td.card(title="Data View Info"):
        td.table(data, pagination=False)
