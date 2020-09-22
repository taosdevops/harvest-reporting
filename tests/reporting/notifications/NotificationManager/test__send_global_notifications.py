import pytest

import reporting.notifications


@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_assert, recipient_type", [("_send_slack_channels", "slack"), ("_send_teams_channels", "teams"), ("_send_email_channels", "emails")])
def test__send_global_notifications__single_recipient_type_populated__assert_method_call_count(num_of_recipients, expected_calls, method_to_assert, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_global_notifications

    mock_notification_manager_recipients_field = getattr(mock_reporting_notifications_NotificationManager.recipients, recipient_type)
    for i in range(expected_calls):
        mock_notification_manager_recipients_field.append("recipient")

    mock_reporting_notifications_NotificationManager.customers = [mock_harvestapi_customer_HarvestCustomer]
    
    mock_reporting_notifications_NotificationManager._send_global_notifications()
    
    assert getattr(mock_reporting_notifications_NotificationManager, method_to_assert).call_count == expected_calls


@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_assert", ["_send_slack_channels", "_send_teams_channels", "_send_email_channels"])
def test__send_global_notifications__all_recipient_types_populated__assert_method_call_count(num_of_recipients, expected_calls, method_to_assert, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
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
