import typing
from typing_extensions import Unpack
from instaui import ui
from instaui_tdesign import td
from instaui_tdesign.components.select import TSelectProps
from pybi.core.data_view import DataField
from pybi.core import _utils
from pybi.core.sql_store import get_sql

_DEFAULT_PROPS = {
    "clearable": True,
}


def select(
    options: DataField,
    value: typing.Optional[typing.Union[str, int]] = None,
    **kwargs: Unpack[TSelectProps],
):
    cp_id = _utils.gen_component_id()
    options = options.distinct()
    field = options.field
    sid = options.sql_id

    options.bind_component(cp_id)
    filter_result, dataset = _utils.filterable(options)

    select_changed = ui.js_event(
        inputs=[
            ui.event_context.e(),
            field,
            cp_id,
            *filter_result.event_inputs,
        ],
        outputs=[filter_result.event_output],
        code=r"""(value, field, cp_id, central, filters, filter_target_id)=> {
if (!central) return;
        
if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) {
    return central.removeFilters(filters, cp_id, filter_target_id);
}

const realValue = Array.isArray(value)? value : [value];
const expr = `${field} in ?`
return central.addFilters(filters, cp_id, filter_target_id, field, expr, realValue);

}""",
    )

    sourceable_result, _ = _utils.sourceable(options, cp_id)

    @ui.computed(
        inputs=[
            cp_id,
            sid,
            *sourceable_result.inputs,
        ]
    )
    def select_options(
        cp_id: str,
        sql_id: str,
        sql_table: dict,
        filters: dict,
        *_: typing.Any,
    ) -> list[str]:
        sql, params = get_sql(
            sql_id, sql_table=sql_table, filters=filters, exclude_components=[cp_id]
        )

        return [row[0] for row in dataset.query(sql, params)["values"]]

    props = {**_DEFAULT_PROPS, **kwargs}

    return td.select(select_options, value=value, label=f"{field}:", **props).on_change(
        select_changed
    )
