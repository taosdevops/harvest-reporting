import pytest

import reporting.notifications


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