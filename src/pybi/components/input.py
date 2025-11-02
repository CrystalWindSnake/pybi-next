import typing
from typing_extensions import Unpack
from instaui import ui
from instaui_tdesign import td
from instaui_tdesign.components.input import TInputProps
from pybi.core.data_view import DataField
from pybi.core import _utils

_DEFAULT_PROPS = {
    "clearable": True,
}


def input(
    field_data: DataField,
    *,
    value: typing.Optional[str] = None,
    **kwargs: Unpack[TInputProps],
):
    cp_id = _utils.gen_component_id()
    field = field_data.field
    query = field_data.build_query()
    query.bind_component(cp_id)

    filter_result, _ = _utils.filterable(
        query, filter_target_id=field_data.source.sql_id
    )

    input_changed = ui.js_event(
        inputs=[
            ui.event_context.e(),
            field,
            cp_id,
            *filter_result.event_inputs,
        ],
        outputs=[filter_result.event_output],
        code=r"""(value, field, cp_id, central, filters, filter_target_id)=> {
        if (!central) return;
        value = value.trim()
        if (value && value.length > 0) {
            value = `%${value.trim()}%`
            const expr = `${field} like ?`
            return central.addFilters(filters, cp_id, filter_target_id, field, expr, value);
        }

        return central.removeFilters(filters, cp_id, filter_target_id);
        }""",
    )

    props = {**_DEFAULT_PROPS, **kwargs}
    td.input(label=f"{field}:", **props).on_change(input_changed)
