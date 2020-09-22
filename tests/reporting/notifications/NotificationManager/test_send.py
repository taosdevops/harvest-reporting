import pytest
import reporting.notifications


@pytest.mark.parametrize("num_of_customers", [0, 1, 2])
@pytest.mark.parametrize("method_to_assert", ["_send_customer_notifications", "_send_global_notifications"])
def test_assert_method_call_count(num_of_customers, method_to_assert, mock_reporting_notifications_NotificationManager, mock_harvestapi_customer_HarvestCustomer):
    del mock_reporting_notifications_NotificationManager.send
    for i in range(num_of_customers):
        mock_reporting_notifications_NotificationManager.customers.append(mock_harvestapi_customer_HarvestCustomer)
    mock_reporting_notifications_NotificationManager.send()
    expected_calls = 1 if method_to_assert == "_send_global_notifications" else num_of_customers
    assert getattr(mock_reporting_notifications_NotificationManager, method_to_assert).call_count == expected_calls