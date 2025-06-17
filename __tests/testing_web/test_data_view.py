from __tests.testing_web.context import Context
from __tests.testing_web.memory_db import MemoryDb
from instaui import ui
import pandas as pd
import pybi
from __tests.utils import Table, Select, display, ListBox


def test_base(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "foo", "bar"], "Age": [18, 19, 20]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv1 = pybi.data_view(f"SELECT Name, AVG(Age) as Age FROM {table} GROUP BY Name")
        pybi.table(dv1)

    context.open()

    Table(context).should_values_any_cell("18.5")


def test_upstream_data_view_update_affects_downstream(
    context: Context, memory_db: MemoryDb
):
    data = {"Name": ["foo", "foo", "bar"], "Age": [18, 19, 20]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv1 = pybi.data_view(f"SELECT * FROM {table}")
        dv2 = pybi.data_view(f"SELECT * FROM {dv1}")

        pybi.select(dv1["Name"])
        pybi.table(dv2)

    context.open()

    table = Table(context)
    select = Select(context)

    table.should_rows_count(3)
    select.select_item("foo")
    table.should_rows_count(2)
    table.should_values_any_cell("foo")
    table.should_values_not_any_cell("bar")


def test_selected_multiple_columns(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo"], "Age": [18], "class": [1]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv1 = pybi.data_view(f"SELECT * FROM {table}")
        pybi.table(dv1[["Name", "Age"]])

    context.open()
    table = Table(context)

    table.should_values_any_cell("foo", "18")
    table.should_values_not_any_cell("1")


def test_computed_binding(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"], "Age": [18, 19]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        @ui.computed(inputs=[dv])
        def value_r0_c0(source):
            return source["values"][0][0]

        ui.label(value_r0_c0)

    context.open()
    context.should_see("foo")


def test_selected_column_computed_binding(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        display.list_box(dv["Name"])

    context.open()
    ListBox(context).should_have_text(["foo", "bar"])
