import os
from unittest.mock import MagicMock, patch
import pytest
import reporting.config
import harvestreporting
# TODO: add `harvestreporting.utils.gcp.secretmanager.get_from_secret_manager` to conftest.py
def test_environment_var_exists():
    fake_environment_var_key = "FAKE1"
    fake_environment_var_value = "I_EXIST"
    os.environ[fake_environment_var_key] = fake_environment_var_value
    assert reporting.config.get_env_var_or_fetch_from_secret_manager(fake_environment_var_key) == fake_environment_var_value

def test_secret_manager_is_called_successfully():
    fake_environment_var_key = "FAKE2"
    harvestreporting.utils.gcp.secretmanager.get_from_secret_manager = MagicMock()
    reporting.config.get_env_var_or_fetch_from_secret_manager(fake_environment_var_key)
    harvestreporting.utils.gcp.secretmanager.get_from_secret_manager.assert_called()

def test_secret_manager_is_called_exception():
    fake_environment_var_key = "FAKE3"
    harvestreporting.utils.gcp.secretmanager.get_from_secret_manager = MagicMock()
    harvestreporting.utils.gcp.secretmanager.get_from_secret_manager.side_effect = Exception
    assert reporting.config.get_env_var_or_fetch_from_secret_manager(fake_environment_var_key) == "NOT_SET"
