"""
CexTrader Exception Testing
"""

import pytest

from dxsp import DexSwap
from dxsp.config import settings


@pytest.fixture(scope="session", autouse=True)
def set_test_settings():
    settings.configure(FORCE_ENV_FOR_DYNACONF="exception")


@pytest.mark.asyncio
async def test_module_exception(caplog):
    result = DexSwap()
    print(result)
    assert any(
        record.message == "Module is disabled. No Client will be created."
        for record in caplog.records
        if record.levelname == "INFO"
    )


# @pytest.mark.asyncio
async def test_create_client_exception(caplog):
    settings.dxsp_enabled = True
    test_class = DexSwap()
    result = test_class._create_client()
    print(result)
    assert result is not None
    assert any(
        record.message
        == "No Client were created. Check your settings or disable the module."
        for record in caplog.records
        if record.levelname == "WARNING"
    )
