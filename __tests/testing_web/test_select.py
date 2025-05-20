from __tests.testing_web.context import Context
from instaui import ui
import pandas as pd
import pybi
from __tests.utils import Select


def test_options(context: Context):
    data = {"Name": ["foo", "foo", "bar"]}

    dataset = pybi.duckdb.from_pandas({"df": pd.DataFrame(data)})

    @context.register_page
    def index():
        table = dataset["df"]
        pybi.select(table["Name"])

    context.open()

    expect_options = Select(context).options()
    expect_options.should_have_count(2)
    expect_options.should_have_text("foo", "bar")
