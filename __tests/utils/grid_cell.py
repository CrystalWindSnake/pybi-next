from typing import List, Union
from playwright.sync_api import Page, expect
from __tests.screen import BaseContext


class GridCell:
    def __init__(
        self,
        context_or_page: Union[BaseContext, Page],
        target_selector: str = ".pybi-test-grid-cell",
    ):
        self.__page = (
            context_or_page
            if isinstance(context_or_page, Page)
            else context_or_page.page
        )
        self.__target_selector = target_selector
        self.__page.locator(self.__target_selector).wait_for(state="visible")

    def _locator_listitem(self):
        selecotor = f"{self.__target_selector} li"
        return self.__page.locator(selecotor)

    def should_have_rows(self, count: int):
        expect(self._locator_listitem()).to_have_count(count)
        return self

    def should_have_text(self, texts: List[List[str]]):
        actual_data = []
        for row in self._locator_listitem().all():
            actual_row = []
            for cell in row.locator("*").all():
                actual_row.append(cell.text_content())
            actual_data.append(actual_row)

        assert actual_data == texts
        return self
