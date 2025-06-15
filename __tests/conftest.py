import pytest
from playwright.sync_api import sync_playwright
import os


HEADLESS = "GITHUB_ACTION" in os.environ


@pytest.fixture(scope="session")
def browser():
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=HEADLESS, timeout=3000)
    yield browser
    browser.close()
    pw.stop()
