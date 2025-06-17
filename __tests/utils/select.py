from typing import Union
from playwright.sync_api import Page, expect
import re

from __tests.screen import BaseContext


_OPTIONS_SELECTOR = ".arco-select-dropdown"
_OPTIONS_ITEM_SELECTOR = f"{_OPTIONS_SELECTOR} ul > li"
_OPTIONS_ITEM_SELECTED_SELECTOR = (
    f"{_OPTIONS_ITEM_SELECTOR}.arco-select-option-selected"
)
_SELECT_OPTION_OPENED_CLASS = "arco-select-view-opened"
_CLEAR_BTN_SELECTOR = ".arco-select-view-clear-btn"


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

        return self

    def __click(self):
        self.__page.click(self.__target_selector)

    def should_options_have_count(self, count: int):
        expect(self.__page.locator(_OPTIONS_ITEM_SELECTOR)).to_have_count(count)
        return self

    def should_options_have_text(self, *texts: str):
        self.should_options_have_count(len(texts))

        real_texts = self.__page.locator(_OPTIONS_ITEM_SELECTOR).all_text_contents()

        assert len(set(texts).difference(real_texts)) == 0, (
            f"Expected texts {texts} not found in {real_texts}"
        )
        return self

    def should_options_have_text_with_order(self, *texts: str):
        expect(self.__page.locator(_OPTIONS_ITEM_SELECTOR)).to_have_text(list(texts))
        return self

    def should_selected(self, *texts: str):
        self.open_options()
        expect(self.__page.locator(_OPTIONS_ITEM_SELECTED_SELECTOR)).to_have_text(
            list(texts)
        )

    def select_item(self, *texts: str):
        """
        .. code-block:: python
        # if foo and bar not selected, click them
        select.select_item("foo", "bar")

        """
        self.open_options()

        for text in texts:
            self.__page.locator(
                f"{_OPTIONS_SELECTOR} ul > li.arco-select-option"
            ).filter(has_text=re.compile(f"^{text}$")).click()

        return self

    def click_items(self, *texts: str):
        """
        .. code-block:: python
        # only click foo and bar whatever they are selected or not
        select.click_items("foo", "bar")

        """
        self.open_options()

        for text in texts:
            self.__page.locator(
                f"{_OPTIONS_SELECTOR} ul > li.arco-select-option"
            ).filter(has_text=re.compile(f"^{text}$")).click()

        return self

    def click_clear_btn(self):
        self.__page.locator(self.__target_selector).hover()
        self.__page.click(f"{self.__target_selector} {_CLEAR_BTN_SELECTOR}")

    def should_not_selected_any(self):
        self.open_options()
        selected_items = self.__page.locator(_OPTIONS_ITEM_SELECTED_SELECTOR)
        expect(selected_items).to_have_count(0)
