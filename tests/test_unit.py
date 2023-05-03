import pytest
from unittest.mock import Mock, patch, MagicMock
from dxsp import DexSwap

@pytest.fixture
def dex_swap():
    return DexSwap(chain_id=1)

