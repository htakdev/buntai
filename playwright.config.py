import pytest

def pytest_configure(config):
    """Playwrightの設定"""
    config.addinivalue_line(
        "markers",
        "playwright: mark test to run with playwright"
    )

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """ブラウザコンテキストの設定"""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        "ignore_https_errors": True,
    } 