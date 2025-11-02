from typing import List, Union
from instaui import html, ui
from pybi.core._mixins import DataSetMixin
from pybi.core.data_field import DataField


def list_box(data: Union[List, DataField], classes: str = "pybi-test-list-box"):
    data = data.flat_values() if isinstance(data, DataField) else data
    html.ul.from_list(data).classes(classes)


def grid_cells(data: DataSetMixin, classes: str = "pybi-test-grid-cell"):
    with html.ul().classes(classes):
        with html.li():
            with ui.vfor(data.columns()) as col:
                ui.label(col)

        with ui.vfor(data.values()) as rows:
            with html.li():
                with ui.vfor(rows) as cell:
                    ui.label(cell)
