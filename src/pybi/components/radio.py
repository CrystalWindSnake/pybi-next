from typing import Any
from typing_extensions import Unpack
from instaui import ui
from instaui_tdesign import td
from instaui_tdesign.components.radio import TRadioGroupProps
from pybi.core.data_view import DataField
from pybi.core import _utils
from pybi.core.sql_store import get_sql

_DEFAULT_PROPS = {}


def radio(
    options: DataField,
    **kwargs: Unpack[TRadioGroupProps],
):
    options = options.distinct().order_by()
    cp_id = _utils.gen_component_id()
    field = options.field
    query = options.build_query()

    sid = query.sql_id
    query.bind_component(cp_id)

    filter_result, dataset = _utils.filterable(
        query, filter_target_id=options.source.sql_id
    )

    radio_changed = ui.js_event(
        inputs=[
            ui.event_context.e(),
            field,
            cp_id,
            *filter_result.event_inputs,
        ],
        outputs=[filter_result.event_output],
        code=r"""(value, field, cp_id, central, filters, filter_target_id)=> {
if (!central) return;
if (value === null || value === undefined || value === '') {
    return central.removeFilters(filters, cp_id, filter_target_id);
}

const realValue = Array.isArray(value)? value : [value];
const expr = `${field} in ?`
return central.addFilters(filters, cp_id, filter_target_id, field, expr, realValue);

}""",
    )

    sourceable_result, _ = _utils.sourceable(query, cp_id)

    @ui.computed(
        inputs=[
            cp_id,
            sid,
            *sourceable_result.inputs,
        ]
    )
    def radio_group_options(
        cp_id: str,
        sql_id: str,
        sql_table: dict,
        filters: dict,
        *_: Any,
    ) -> list[dict]:
        sql, params = get_sql(
            sql_id, sql_table=sql_table, filters=filters, exclude_components=[cp_id]
        )

        return [
            {
                "label": row[0],
                "value": row[0],
            }
            for row in dataset.query(sql, params)["values"]
        ]

    props = {**_DEFAULT_PROPS, **kwargs}

    return td.radio_group(options=radio_group_options, **props).on_change(radio_changed)
