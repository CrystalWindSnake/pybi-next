from typing import List, Union
from instaui import html, ui
from pybi.link_sql._mixin import DataColumnMixin, DataTableMixin


def list_box(data: Union[List, DataColumnMixin], classes: str = "pybi-test-list-box"):
    html.ul.from_list(data).classes(classes)


def grid_cells(data: DataTableMixin, classes: str = "pybi-test-grid-cell"):
    with html.ul().classes(classes):
        with html.li():
            with ui.vfor(data.columns()) as col:
                ui.label(col)

        with ui.vfor(data.values()) as rows:
            with html.li():
                with ui.vfor(rows) as cell:
                    ui.label(cell)
