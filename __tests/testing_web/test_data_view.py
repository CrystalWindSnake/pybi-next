from __tests.testing_web.context import Context
from instaui import ui
import pandas as pd
import pybi
from __tests.utils import Table


def test_base(context: Context):
    data = {"Name": ["foo", "foo", "bar"], "Age": [18, 19, 20]}

    dataset = pybi.duckdb.from_pandas({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv1 = pybi.data_view(f"SELECT Name, AVG(Age) as Age FROM {table} GROUP BY Name")
        pybi.table(dv1)

    context.open()

    Table(context).should_values_any_cell("18.5")


def test_selected_multiple_columns(context: Context):
    data = {"Name": ["foo"], "Age": [18], "class": [1]}

    dataset = pybi.duckdb.from_pandas({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv1 = pybi.data_view(f"SELECT * FROM {table}")
        pybi.table(dv1[["Name", "Age"]])

    context.open()
    table = Table(context)

    table.should_values_any_cell("foo", "18")
    table.should_values_not_any_cell("1")


def test_computed_binding(context: Context):
    data = {"Name": ["foo", "bar"], "Age": [18, 19]}

    dataset = pybi.duckdb.from_pandas({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        @ui.computed(inputs=[dv])
        def result(names):
            return str(names)

        pybi.label(result)

    context.open()
    context.should_see("[['foo', 18], ['bar', 19]]", equal_to=True)


def test_selected_column_computed_binding(context: Context):
    data = {"Name": ["foo", "bar"]}

    dataset = pybi.duckdb.from_pandas({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        dv = pybi.data_view(f"SELECT * FROM {table}")

        @ui.computed(inputs=[dv["Name"]])
        def result(names):
            return str(names)

        pybi.label(result)

    context.open()
    context.should_see("['foo', 'bar']", equal_to=True)
