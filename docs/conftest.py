import os

import pytest


@pytest.fixture
def clear_plugins_dir_env():
    yield
    os.environ.pop("PRODUCT_REVIEWS_PLUGINS_DIR", None)
