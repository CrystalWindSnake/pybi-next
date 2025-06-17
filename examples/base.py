import pybi
from instaui import ui
import pandas as pd
from templates import make_bar, make_line, make_pie


data = {
    "Class": [
        "Class 1",
        "Class 1",
        "Class 1",
        "Class 1",
        "Class 1",
        "Class 2",
        "Class 2",
        "Class 2",
        "Class 2",
        "Class 2",
        "Class 3",
        "Class 3",
        "Class 3",
        "Class 3",
        "Class 3",
    ],
    "Name": [
        "Zhang Wei",
        "Li Fang",
        "Wang Na",
        "Zhao Min",
        "Chen Jing",
        "Sun Jie",
        "Wu Yong",
        "Zhou Yan",
        "Xu Lei",
        "He Yang",
        "Liu Qiang",
        "Zhu Li",
        "Qin Feng",
        "You Wen",
        "Rong Xuan",
    ],
    "Age": [18, 19, 20, 21, 22, 18, 19, 20, 21, 22, 18, 19, 20, 21, 22],
}

dataset = pybi.duckdb.from_pandas({"df": pd.DataFrame(data)})


@ui.page()
def index():
    table = dataset["df"]

    gp_query = pybi.query(
        f"SELECT name, ROUND(avg(Age),2) as Age FROM {table} GROUP BY name",
    )

    with pybi.grid(columns=pybi.grid.auto_columns(min_width="20vw")).classes(
        "min-h-[300px]"
    ):
        pybi.echarts(make_bar(table, x="Name", y="Age", agg="avg"))
        pybi.echarts(make_line(table, x="Name", y="Age", agg="avg"))
        pybi.echarts(make_pie(table, name="Class", value="Age", agg="sum"))

    with pybi.grid().classes("max-w-[800px] mx-auto gap-2"):
        # pybi.echarts(make_bar(table, x="name", y="age"))
        pybi.select(table["Class"])
        pybi.select(table["name"], multiple=True)
        pybi.table(gp_query)


ui.server(debug=True).run()
