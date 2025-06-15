from __future__ import annotations
from typing import TYPE_CHECKING, Dict, cast
from instaui import arco, ui
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from pybi.link_sql.data_view_store import get_store as get_view_store
from pybi.link_sql import sql_stem


if TYPE_CHECKING:
    from pybi.link_sql.data_view import DataView


class QueryMap(ElementBindingMixin, ObservableMixin):
    def __init__(self) -> None:
        self._sql_map = get_view_store().sql_map

    def get_filters(self, view: DataView):
        return get_view_store().get_filters(view.name)

    def _to_observable_config(self):
        return cast(ObservableMixin, self._sql_map)._to_observable_config()

    def _to_element_binding_config(self) -> Dict:
        return cast(ElementBindingMixin, self._sql_map)._to_element_binding_config()

    def display_table(self):
        @ui.computed(inputs=[self._sql_map])
        def table_data(sql_map: Dict[str, Dict]):
            columns = ["name", "sql", "type", "filters", "parents"]
            values = [
                dict(
                    zip(
                        columns,
                        [
                            name,
                            data["sql"],
                            sql_stem.get_source_type(name),
                            str(data["filters"]),
                            str(data["parents"]),
                        ],
                    )
                )
                for name, data in sql_map.items()
            ]

            real_cols = [
                {"title": col, "dataIndex": col, "ellipsis": True, "tooltip": True}
                for col in columns
            ]

            return {"columns": real_cols, "data": values}

        arco.table(columns=table_data["columns"], data=table_data["data"])
