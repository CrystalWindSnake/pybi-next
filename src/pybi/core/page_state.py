from instaui import ui
from .pybi_central.central import PybiCentral
from .sql_store import SqlStore
from ._component_store import ComponentStore


class PageState(ui.PageState):
    def __init__(self) -> None:
        self.central = PybiCentral()
        self.sql_store = SqlStore()
        self.component_store = ComponentStore()
