import logging
import os
from unittest.mock import MagicMock
import pytest

import reporting
from harvestapi.customer import HarvestCustomer
import taosdevopsutils
import pymsteams


def mock_all_obj_methods(instantiated_obj):
    for method in dir(instantiated_obj):
        if not method.startswith("__") and callable(getattr(instantiated_obj, method)):
            setattr(instantiated_obj, method, MagicMock())
        else:
            continue
    return instantiated_obj


@pytest.fixture(scope="function")
def mock_reporting_config_VerificationConfig():
    mock_VerificationConfig = reporting.config.VerificationConfig(
        email=list(),
        slack=list(),
        teams=list()
    )
    return mock_VerificationConfig


@pytest.fixture(scope="function")
def mock_reporting_config_RecipientsConfig(mock_reporting_config_VerificationConfig):
    mock_RecipientsConfig = reporting.config.RecipientsConfig(sendVerificationConfig=mock_reporting_config_VerificationConfig)
    return mock_RecipientsConfig


@pytest.fixture(scope="function")
def mock_reporting_config_Recipients_with_config(mock_reporting_config_RecipientsConfig):
    mock_Recipients = reporting.config.Recipients(config=mock_reporting_config_RecipientsConfig)
    return mock_Recipients


@pytest.fixture(scope="function")
def mock_reporting_config_Recipients_without_config():
    mock_Recipients = reporting.config.Recipients()
    return mock_Recipients


@pytest.fixture(scope="function")
def mock_reporting_config_Recipients_without_config_factory():
    class RecipientsFactory(reporting.config.Recipients):
        def generate(self):
            return reporting.config.Recipients()
    return RecipientsFactory()


@pytest.fixture(scope="function")
def mock_reporting_config_Customer(mock_reporting_config_Recipients_without_config):
    mock_Customer = reporting.config.Customer(
        name="Mock Customer",
        hours=80,
        recipients=mock_reporting_config_Recipients_without_config
    )
    return mock_Customer


@pytest.fixture(scope="function")
def mock_taosdevopsutils_slack_Slack():
    mock_slack_client = taosdevopsutils.slack.Slack
    mock_slack_client = MagicMock()
    return mock_slack_client


@pytest.fixture(scope="function")
def mock_pymsteams_connectorcard():
    mock_pymsteams_connectorcard = pymsteams.connectorcard
    mock_pymsteams_connectorcard = MagicMock()
    return mock_pymsteams_connectorcard


@pytest.fixture(scope="function")
def mock_harvestapi_customer_HarvestCustomer(mock_reporting_config_Customer, mock_reporting_config_Recipients_without_config):
    mock_HarvestCustomer = HarvestCustomer(
        client=MagicMock(), 
        config=mock_reporting_config_Customer,
        recipients=mock_reporting_config_Recipients_without_config,
        customer=MagicMock())
    return mock_HarvestCustomer


@pytest.fixture(scope="function")
def mock_reporting_notifications_NotificationManager(mock_taosdevopsutils_slack_Slack, mock_reporting_config_Recipients_without_config_factory):
    mock_nm = reporting.notifications.NotificationManager(
        customers = list(),
        global_recipients = mock_reporting_config_Recipients_without_config_factory.generate(),
        exception_config = mock_reporting_config_Recipients_without_config_factory.generate(),
        sendgrid_api_key = "testsendgridapikey",
        from_email = "test@testymctestface.com"
    )
    mock_nm.slack_client = mock_taosdevopsutils_slack_Slack
    assert isinstance(mock_nm.slack_client, MagicMock)
    assert mock_nm.recipients.config
    assert mock_nm.exception_config.config
    mock_nm = mock_all_obj_methods(mock_nm)
    return mock_nm