from typing import Union
from playwright.sync_api import Page, expect
import re

from __tests.screen import BaseContext


class Table:
    def __init__(
        self, context_or_page: Union[BaseContext, Page], selector: str = "table"
    ):
        self.__page = (
            context_or_page
            if isinstance(context_or_page, Page)
            else context_or_page.page
        )
        self.__selector = selector

    def one_cell(self):
        return Table(self.__page, f"{self.__selector} td")

    def should_see(self, *texts: str):
        for text in texts:
            target = self.__page.locator(self.__selector).filter(has_text=text)
            expect(target).to_have_count(1)

    def should_not_see(self, *texts: str):
        for text in texts:
            target = self.__page.locator(self.__selector).filter(
                has_text=re.compile(f"^{text}$", re.IGNORECASE)
            )
            expect(target).to_have_count(0)
