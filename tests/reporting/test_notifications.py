import os
import unittest
import unittest.mock
from unittest.mock import MagicMock
import pytest

import reporting.notifications
from harvestapi.customer import HarvestCustomer
import reporting.config
from reporting.config import Recipients
import pymsteams

CUSTOM_EXCEPTION_PARAMS = {
    "SlackSendError": {"channel": "#test", "message": "uh-oh"},
    "TeamsSendError": {"channel": "#test"},
    "EmailSendError": {"channels": "#test", "message": "uh-oh"},
    }

@pytest.mark.parametrize("num_of_customers", [0, 1, 2])
@pytest.mark.parametrize("method_to_assert", ["_send_customer_notifications", "_send_global_notifications"])
def test_Given_numOfCustomersANDMethodToAssert_When_send_Then_methodToAssertCallCountWillEqualNumOfCustomers(num_of_customers, method_to_assert, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager.send
    for i in range(num_of_customers):
        mock_reporting_notifications_NotificationManager.customers.append(mock_harvestapi_customer_HarvestCustomer)
    mock_reporting_notifications_NotificationManager.send()
    expected_calls = 1 if method_to_assert == "_send_global_notifications" else num_of_customers
    assert getattr(mock_reporting_notifications_NotificationManager, method_to_assert).call_count == expected_calls


@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_assert, recipient_type", [("_send_slack_channels", "slack"), ("_send_teams_channels", "teams"), ("_send_email_channels", "emails")])
def test_Given_numberOfRecipientsANDPreferredContactMethod_When__send_customer_notifications_Then_methodToAssertCallCountEqualsExpectedCalls(num_of_recipients, expected_calls, method_to_assert, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_customer_notifications

    for i in range(num_of_recipients):
        mock_harvest_customer_recipients_field = getattr(mock_harvestapi_customer_HarvestCustomer.recipients, recipient_type)
        mock_harvest_customer_recipients_field.append("recipient")

    mock_reporting_notifications_NotificationManager._send_customer_notifications(mock_harvestapi_customer_HarvestCustomer)
    assert getattr(mock_reporting_notifications_NotificationManager, method_to_assert).call_count == expected_calls


@pytest.mark.parametrize("method_to_raise_at,exception_to_raise,recipient_type", [
    ("_send_slack_channels", "SlackSendError", "slack"), 
    ("_send_teams_channels","TeamsSendError", "teams"), 
    ("_send_email_channels","EmailSendError", "emails")
    ])
def test_Given_methodToRaiseExceptionAtANDExceptionToRaiseANDRecipientTtype_When__send_customer_notifications_Then_sendExceptionToExceptionChannels(method_to_raise_at, exception_to_raise, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_customer_notifications

    mock_harvest_customer_recipients_field = getattr(mock_harvestapi_customer_HarvestCustomer.recipients, recipient_type)
    mock_harvest_customer_recipients_field.append("recipients")

    exception_func = getattr(reporting.notifications, exception_to_raise)

    mock_nm_method = getattr(mock_reporting_notifications_NotificationManager, method_to_raise_at)
    mock_nm_method.side_effect = exception_func(**CUSTOM_EXCEPTION_PARAMS[exception_to_raise])

    mock_reporting_notifications_NotificationManager._send_customer_notifications(mock_harvestapi_customer_HarvestCustomer)
    mock_reporting_notifications_NotificationManager._send_exception_channels.assert_called_once()


@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_assert, recipient_type", [("_send_slack_channels", "slack"), ("_send_teams_channels", "teams"), ("_send_email_channels", "emails")])
def test_Given_numberOfRecipientsANDExpectedCallCountANDMethodToAssertANDRecipientType_When__send_global_notifications_Then_callMethodToAssert(num_of_recipients, expected_calls, method_to_assert, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_global_notifications

    mock_notification_manager_recipients_field = getattr(mock_reporting_notifications_NotificationManager.recipients, recipient_type)
    for i in range(expected_calls):
        mock_notification_manager_recipients_field.append("recipient")

    mock_reporting_notifications_NotificationManager.customers = [mock_harvestapi_customer_HarvestCustomer]
    
    mock_reporting_notifications_NotificationManager._send_global_notifications()
    
    assert getattr(mock_reporting_notifications_NotificationManager, method_to_assert).call_count == expected_calls


@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_assert", ["_send_slack_channels", "_send_teams_channels", "_send_email_channels"])
def test_Given_numberOfRecipientsANDExpectedCallCountANDMethodToAssert_When__send_global_notificationsANDmanyPreferredContactMethods_Then_assertNoMethodToAssertIsSkipped(num_of_recipients, expected_calls, method_to_assert, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_global_notifications

    for field in mock_reporting_notifications_NotificationManager.recipients.__dataclass_fields__:
        field = getattr(mock_reporting_notifications_NotificationManager.recipients, field)
        if type(field) == list:
            for i in range(num_of_recipients):
                field.append("recipient")

    mock_reporting_notifications_NotificationManager.customers = [mock_harvestapi_customer_HarvestCustomer]
    
    mock_reporting_notifications_NotificationManager._send_global_notifications()
    
    assert getattr(mock_reporting_notifications_NotificationManager, method_to_assert).call_count == expected_calls


@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_raise_at, recipient_type", [("_send_slack_channels", "slack"), ("_send_teams_channels", "teams"), ("_send_email_channels", "emails")])
def test_Given_numberOfRecipientsANDExpectedCallCountANDMethodToRaiseAtANDRecipientType_When__unableToSendViaPreferredContactMethod_Then__send_exception_channels(num_of_recipients, expected_calls, method_to_raise_at, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_global_notifications

    mock_notification_manager_recipients_field = getattr(mock_reporting_notifications_NotificationManager.recipients, recipient_type)
    for i in range(expected_calls):
        mock_notification_manager_recipients_field.append("recipient")

    mock_reporting_notifications_NotificationManager.customers = [mock_harvestapi_customer_HarvestCustomer]
    
    method_to_raise_exception_at = getattr(mock_reporting_notifications_NotificationManager, method_to_raise_at)
    method_to_raise_exception_at.side_effect = Exception

    mock_reporting_notifications_NotificationManager._send_global_notifications()
    
    assert mock_reporting_notifications_NotificationManager._send_exception_channels.call_count == expected_calls


@pytest.mark.parametrize("customer_passed", [True, False])
@pytest.mark.parametrize("method_to_assert, recipient_type", [("_send_slack_channels", "slack"), ("_send_teams_channels", "teams"), ("_send_email_channels", "emails")])
def test_Given_customerPassedANDmethodToAssertANDRecipientType_When_notificationManagerExceptionConfigPopulated_Then_assertMethodToAssertIsCalled(customer_passed, method_to_assert, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_exception_channels

    mock_harvest_customer_recipients_field = getattr(mock_reporting_notifications_NotificationManager.exception_config, recipient_type)
    mock_harvest_customer_recipients_field.append("recipient")

    mock_reporting_notifications_NotificationManager._send_exception_channels(
        e=Exception, 
        customer=mock_harvestapi_customer_HarvestCustomer if customer_passed else None)

    getattr(mock_reporting_notifications_NotificationManager, method_to_assert).assert_called_once()


@pytest.mark.parametrize("num_of_channels", [0, 1, 2])
def test_Given_numberOfChannelsANDsuccessfulResponse_When__send_slack_channelsIsCalled_Then_postSlackMessageToChannelCallCountIsEqualToNumberOfChannels(num_of_channels, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_slack_channels
    mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.return_value = {"status_code": 200}

    channels = list()
    for i in range(num_of_channels):
        channels.append("channel")

    mock_reporting_notifications_NotificationManager._send_slack_channels(channels=channels, msg="halp")

    assert mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.call_count == num_of_channels


@pytest.mark.parametrize("returned_response", [302, 403, 500, Exception])
def test_Given_badResponseORException_When__send_slack_channelsIsCalled_Then_postSlackMessageToChannelRaisesSlackSendError(returned_response, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_slack_channels
    mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.return_value = {"status_code": returned_response}

    with pytest.raises(reporting.notifications.SlackSendError):
        mock_reporting_notifications_NotificationManager._send_slack_channels(channels=["channel"], msg="halp")


# struggle bussing to mock out the import of pymsteams
# @pytest.mark.parametrize("num_of_channels", [0, 1, 2])
# def test_Given_numberOfChannelsANDsuccessfulResponse_When__send_teams_channelsIsCalled_Then_postTeamsMessageToChannelCallCountIsEqualToNumberOfChannels(num_of_channels, mock_pymsteams_connectorcard, mock_reporting_notifications_NotificationManager):
#     del mock_reporting_notifications_NotificationManager._send_teams_channels
#     # mock_pymsteams.connectorcard.return_value = MagicMock()
#     # mock_pymsteams.connectorcard.return_value.send = True
#     # mock_pymsteams = reporting.notifications.pymsteams #no
#     # mock_pymsteams = MagicMock() # no
#     mock_pymsteams_connectorcard = pymsteams.connectorcard
#     # mock_pymsteams = MagicMock()
#     # mock_pymsteams_connectorcard.return_value = MagicMock()
#     # mock_pymsteams_connectorcard.send.return_value = True


#     channels = list()
#     for i in range(num_of_channels):
#         channels.append("channel")

#     mock_reporting_notifications_NotificationManager._send_teams_channels(channels=channels, msg="halp")

#     assert mock_pymsteams.connectorcard.send.call_count == num_of_channels


# @pytest.mark.parametrize("returned_response", [302, 403, 500, Exception])
# def test_Given_badResponseORException_When__send_teams_channelsIsCalled_Then_postTeamsMessageToChannelRaisesSlackSendError(returned_response, mock_reporting_notifications_NotificationManager):
#     del mock_reporting_notifications_NotificationManager._send_slack_channels
#     mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.return_value = {"status_code": returned_response}

#     with pytest.raises(reporting.notifications.SlackSendError):
#         mock_reporting_notifications_NotificationManager._send_slack_channels(channels=["channel"], msg="halp")


# @pytest.mark.parametrize("num_of_channels", [0, 1, 2])
# def test_Given_numberOfChannelsANDsuccessfulResponse_When__send_emails_channelsIsCalled_Then_postemailsMessageToChannelCallCountIsEqualToNumberOfChannels(num_of_channels, mock_reporting_notifications_NotificationManager):
#     del mock_reporting_notifications_NotificationManager._send_emails_channels
#     mock_reporting_notifications_NotificationManager.emails_client.post_emails_message.return_value = {"status_code": 200}

#     channels = list()
#     for i in range(num_of_channels):
#         channels.append("channel")

#     mock_reporting_notifications_NotificationManager._send_emails_channels(channels=channels, msg="halp")

#     assert mock_reporting_notifications_NotificationManager.emails_client.post_emails_message.call_count == num_of_channels


# @pytest.mark.parametrize("returned_response", [302, 403, 500, Exception])
# def test_Given_badResponseORException_When__send_emails_channelsIsCalled_Then_postemailsMessageToChannelRaisesemailsSendError(returned_response, mock_reporting_notifications_NotificationManager):
#     del mock_reporting_notifications_NotificationManager._send_emails_channels
#     mock_reporting_notifications_NotificationManager.emails_client.post_emails_message.return_value = {"status_code": returned_response}

#     with pytest.raises(reporting.notifications.emailsSendError):
#         mock_reporting_notifications_NotificationManager._send_emails_channels(channels=["channel"], msg="halp")