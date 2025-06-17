from __tests.testing_web.context import Context
from __tests.testing_web.memory_db import MemoryDb
import pandas as pd
import pybi
from __tests.utils import Select, display, ListBox


def test_options(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "foo", "bar"]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        pybi.select(table["Name"])

    context.open()

    select = Select(context)
    select.should_options_have_count(2)
    select.should_options_have_text("foo", "bar")


def test_no_option_selected(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        pybi.select(dv["Name"])
        display.list_box(dv["name"])

    context.open()
    select = Select(context)
    select.should_not_selected_any()
    ListBox(context).should_have_text(["foo", "bar"])


def test_selection_impact(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        pybi.select(dv["Name"])
        display.list_box(dv["Name"])

    context.open()
    select = Select(context)
    list_box = ListBox(context)
    list_box.should_have_text(["foo", "bar"])
    select.select_item("foo")
    list_box.should_have_text(["foo"])
