import pytest

import reporting.notifications


CUSTOM_EXCEPTION_PARAMS = {
    "SlackSendError": {"channel": "#test", "message": "uh-oh"},
    "TeamsSendError": {"channel": "#test"},
    "EmailSendError": {"channels": "#test", "message": "uh-oh"},
    }

@pytest.mark.parametrize("num_of_recipients, expected_calls", [(0,0), (1,1), (2,1)])
@pytest.mark.parametrize("method_to_assert, recipient_type", [("_send_slack_channels", "slack"), ("_send_teams_channels", "teams"), ("_send_email_channels", "emails")])
def test_assert_method_call_count(num_of_recipients, expected_calls, method_to_assert, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
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
def test_assert_called_on_exception__send_exception_channels(method_to_raise_at, exception_to_raise, recipient_type, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager._send_customer_notifications

    mock_harvest_customer_recipients_field = getattr(mock_harvestapi_customer_HarvestCustomer.recipients, recipient_type)
    mock_harvest_customer_recipients_field.append("recipients")

    exception_func = getattr(reporting.notifications, exception_to_raise)

    mock_nm_method = getattr(mock_reporting_notifications_NotificationManager, method_to_raise_at)
    mock_nm_method.side_effect = exception_func(**CUSTOM_EXCEPTION_PARAMS[exception_to_raise])

    mock_reporting_notifications_NotificationManager._send_customer_notifications(mock_harvestapi_customer_HarvestCustomer)
    mock_reporting_notifications_NotificationManager._send_exception_channels.assert_called_once()