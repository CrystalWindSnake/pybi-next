from typing import Optional
from playwright.sync_api import expect

from __tests.screen import BaseContext


SELECT_BOX_SELECTOR = ".t-select-input.t-select"
OPTIONS_ITEM_SELECTOR = "ul.t-select__list > li"
OPTIONS_ITEM_SELECTED_SELECTOR = f"{OPTIONS_ITEM_SELECTOR}.t-is-selected"


class use_select_controls:
    def __init__(self, context: BaseContext, *, selector: Optional[str] = None) -> None:
        self._context = context

        selector = (
            f"{selector} {SELECT_BOX_SELECTOR}" if selector else SELECT_BOX_SELECTOR
        )
        self._select_box = context.page.locator(selector)
        self._select_input = self._select_box.locator("input")

    def should_value(self, value: str):
        self._context.expect(self._select_input).to_have_value(value)
        return self

    def _try_open_dropdown(self):
        if self._context.page.locator(".t-select__dropdown-inner").count() <= 0:
            self._select_box.click()

    def _try_close_dropdown(self):
        if self._context.page.locator(".t-select__dropdown-inner").count() > 0:
            self._select_box.click()

    def should_options_count(self, count: int):
        self._try_open_dropdown()
        expect(self._context.page.locator(OPTIONS_ITEM_SELECTOR)).to_have_count(count)
        return self

    def select_option(self, option: str):
        self._try_open_dropdown()
        self._context.page.locator(
            f'{OPTIONS_ITEM_SELECTOR}:has-text("{option}")'
        ).click()

    def should_options_have_text(self, *texts: str):
        self.should_options_count(len(texts))

        real_texts = self._context.page.locator(
            OPTIONS_ITEM_SELECTOR
        ).all_text_contents()

        assert len(set(texts).difference(real_texts)) == 0, (
            f"Expected texts {texts} not found in {real_texts}"
        )
        return self

    def should_not_selected_any(self):
        self._try_open_dropdown()
        selected_items = self._context.page.locator(OPTIONS_ITEM_SELECTED_SELECTOR)
        expect(selected_items).to_have_count(0)

    def click_clear_btn(self):
        self._select_input.hover()
        self._select_box.locator("t-input__clear").click()
