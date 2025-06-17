from __tests.testing_web.context import Context
from __tests.testing_web.memory_db import MemoryDb
from instaui import ui
import pandas as pd
import pybi
from __tests.utils import Select


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

        @ui.computed(inputs=[dv["Name"]])
        def result(names):
            return str(names)

        pybi.select(dv["Name"])
        pybi.label(result)

    context.open()
    select = Select(context)
    select.should_not_selected_any()
    context.should_see("['foo', 'bar']", equal_to=True)


def test_selection_impact(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        @ui.computed(inputs=[dv["Name"]])
        def result(names):
            return str(names)

        pybi.select(dv["Name"])
        pybi.label(result)

    context.open()
    select = Select(context)
    context.should_see("['foo', 'bar']", equal_to=True)
    select.select_item("foo")
    context.should_see("['foo']", equal_to=True)
