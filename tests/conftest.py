import logging
import os
from unittest.mock import MagicMock

import pytest
import taosdevopsutils
from google.cloud import pubsub_v1

from reporting.config import VerificationConfig, RecipientsConfig, Recipients, Customer
from harvestapi.customer import HarvestCustomer


def mock_all_obj_methods(instantiated_obj):
    for method in dir(instantiated_obj):
        if not method.startswith("__") and callable(getattr(instantiated_obj, method)):
            setattr(instantiated_obj, method, MagicMock())
        else:
            continue
    return instantiated_obj


@pytest.fixture(scope="function")
def mock_reporting_config_VerificationConfig():
    mock_VerificationConfig = VerificationConfig(
        email=list(),
        slack=list(),
        teams=list()
    )
    return mock_VerificationConfig


@pytest.fixture(scope="function")
def mock_reporting_config_RecipientsConfig(mock_reporting_config_VerificationConfig):
    mock_RecipientsConfig = RecipientsConfig(sendVerificationConfig=mock_reporting_config_VerificationConfig)
    return mock_RecipientsConfig


@pytest.fixture(scope="function")
def mock_reporting_config_Recipients_with_config(mock_reporting_config_RecipientsConfig):
    mock_Recipients = Recipients(config=mock_reporting_config_RecipientsConfig)
    return mock_Recipients


@pytest.fixture(scope="function")
def mock_reporting_config_Recipients_without_config():
    mock_Recipients = Recipients()
    return mock_Recipients


@pytest.fixture(scope="function")
def mock_reporting_config_Recipients_without_config_factory():
    class RecipientsFactory(Recipients):
        def generate(self):
            return Recipients()
    return RecipientsFactory()


@pytest.fixture(scope="function")
def mock_reporting_config_Customer(mock_reporting_config_Recipients_without_config):
    mock_Customer = Customer(
        name="Mock Customer",
        hours=80,
        recipients=mock_reporting_config_Recipients_without_config
    )
    return mock_Customer


# @pytest.fixture(scope="function")
# def mock_google_cloud_pubsub():
#     mock_google_cloud_pubsub = pubsub_v1.PublisherClient
#     mock_google_cloud_pubsub = MagicMock()
#     return mock_google_cloud_pubsub


@pytest.fixture(scope="function")
def mock_harvestapi_customer_HarvestCustomer(mock_reporting_config_Customer, mock_reporting_config_Recipients_without_config):
    mock_HarvestCustomer = HarvestCustomer(
        client=MagicMock(), 
        config=mock_reporting_config_Customer,
        recipients=mock_reporting_config_Recipients_without_config,
        customer=MagicMock())
    return mock_HarvestCustomer


@pytest.fixture(scope="function")
# def mock_reporting_notifications_NotificationManager(mock_google_cloud_pubsub, mock_reporting_config_Recipients_without_config_factory):
def mock_reporting_notifications_NotificationManager(mock_reporting_config_Recipients_without_config_factory):
    mock_nm = reporting.notifications.NotificationManager(
        customers = list(),
        global_recipients = mock_reporting_config_Recipients_without_config_factory.generate(),
        exception_config = mock_reporting_config_Recipients_without_config_factory.generate(),
        sendgrid_api_key = "testsendgridapikey",
        from_email = "test@testymctestface.com"
    )
    # mock_nm.publisher = mock_google_cloud_pubsub
    # assert isinstance(mock_nm.publisher, MagicMock)
    assert mock_nm.recipients.config
    assert mock_nm.exception_config.config
    mock_nm = mock_all_obj_methods(mock_nm)
    return mock_nm
