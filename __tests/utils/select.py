from typing import Union
from playwright.sync_api import Page, expect
import re

from __tests.screen import BaseContext


_OPTIONS_SELECTOR = ".arco-select-dropdown"
_SELECT_OPTION_OPENED_CLASS = "arco-select-view-opened"


class Select:
    def __init__(
        self,
        context_or_page: Union[BaseContext, Page],
        target_selector: str = ".arco-select",
    ):
        self.__page = (
            context_or_page
            if isinstance(context_or_page, Page)
            else context_or_page.page
        )
        self.__target_selector = target_selector

    def open_options(self):
        opened = (
            self.__page.locator(
                f"{self.__target_selector}.{_SELECT_OPTION_OPENED_CLASS}"
            ).count()
            == 1
        )

        if not opened:
            self.__click()

    def __click(self):
        self.__page.click(self.__target_selector)

    def options(self, auto_click: bool = True):
        if auto_click:
            self.open_options()
        return SelectOption(self.__page, _OPTIONS_SELECTOR)


class SelectOption:
    def __init__(self, page: Page, selector: str) -> None:
        self.__page = page
        self.__selector = selector

    def should_have_count(self, count: int):
        expect(self.__page.locator(f"{self.__selector} li")).to_have_count(count)
        return self

    def should_have_text(self, *texts: str):
        self.should_have_count(len(texts))

        real_texts = self.__page.locator(
            f"{self.__selector} ul > li"
        ).all_text_contents()

        assert (
            len(set(texts).difference(real_texts)) == 0
        ), f"Expected texts {texts} not found in {real_texts}"
        return self

    def should_have_text_with_order(self, *texts: str):
        expect(self.__page.locator(f"{self.__selector} ul > li")).to_have_text(
            list(texts)
        )
        return self
