import pytest
from playwright.sync_api import Browser
import duckdb
from __tests.testing_web.context import Context
from __tests.testing_web.server import TestServer
from __tests.testing_web.memory_db import MemoryDb


@pytest.fixture(scope="function")
def context(browser: Browser, start_server: TestServer):
    page = browser.new_page()
    start_server.start()
    start_server.wait_for_connection()

    context = Context(start_server, page)

    yield context

    page.close()


@pytest.fixture(scope="session")
def global_memory_db():
    dataset = MemoryDb()
    yield dataset


@pytest.fixture(scope="function")
def memory_db(global_memory_db: MemoryDb):
    global_memory_db.clear()
    yield global_memory_db


@pytest.fixture(scope="session", autouse=True)
def start_server():
    server = TestServer()
    yield server
    server.stop()


@pytest.fixture(autouse=True, scope="function")
def reset_duckdb_memory_db():
    conn = duckdb.connect(":default:", read_only=False)
    tables = conn.execute("PRAGMA show_tables;").fetchall()
    for table in tables:
        table_name = table[0]
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
    yield
