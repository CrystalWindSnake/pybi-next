from __tests.testing_web.context import Context
from __tests.testing_web.memory_db import MemoryDb
import pandas as pd
from __tests.utils import display, ListBox
import pybi


def test_distinct_from_data_view(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "foo", "bar"], "Age": [18, 19, 20]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        dv1 = dataset["df"]
        display.list_box(dv1["Name"].distinct())

    context.open()
    ListBox(context).should_have_text(["foo", "bar"])


def test_distinct_from_query(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "foo", "bar"], "Age": [18, 19, 20]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        dv1 = dataset["df"]
        query = pybi.query(f"SELECT Name FROM {dv1}")
        display.list_box(query["Name"].distinct())

    context.open()
    ListBox(context).should_have_text(["foo", "bar"])


def test_flat_values_from_data_view(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"], "Age": [18, 19]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        dv1 = dataset["df"]
        display.list_box(dv1["Name"].flat_values())

    context.open()
    ListBox(context).should_have_text(["foo", "bar"])


def test_flat_values_from_query(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"], "Age": [18, 19]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        dv1 = dataset["df"]
        query = pybi.query(f"SELECT Name FROM {dv1}")
        display.list_box(query["Name"].flat_values())

    context.open()
    ListBox(context).should_have_text(["foo", "bar"])
