from typing import List, Union
from playwright.sync_api import Page, expect
from __tests.screen import BaseContext


class ListBox:
    def __init__(
        self,
        context_or_page: Union[BaseContext, Page],
        target_selector: str = ".pybi-test-list-box",
    ):
        self.__page = (
            context_or_page
            if isinstance(context_or_page, Page)
            else context_or_page.page
        )
        self.__target_selector = target_selector

    def _locator_listitem(self):
        selecotor = f"{self.__target_selector} li"
        return self.__page.locator(selecotor)

    def should_have_count(self, count: int):
        expect(self._locator_listitem()).to_have_count(count)
        return self

    def should_have_text(self, texts: List[str]):
        expect(self._locator_listitem()).to_have_text(texts)
        return self
