from __tests.testing_web.context import Context
from __tests.testing_web.memory_db import MemoryDb
import pandas as pd
from __tests.utils import display, ListBox


def test_distinct_from_data_view(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "foo", "bar"], "Age": [18, 19, 20]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        dv1 = dataset["df"]
        display.list_box(dv1["Name"].distinct().order_by())

    context.open()
    ListBox(context).should_have_text(["bar", "foo"])


def test_flat_values_from_data_view(context: Context, memory_db: MemoryDb):
    data = {"Name": ["foo", "bar"], "Age": [18, 19]}
    dataset = memory_db.from_dataframe({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        dv1 = dataset["df"]
        display.list_box(dv1["Name"].flat_values())

    context.open()
    ListBox(context).should_have_text(["foo", "bar"])
