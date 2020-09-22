import pytest

import reporting.notifications


@pytest.mark.parametrize("num_of_channels", [0, 1, 2])
def test_assert_call_count_post_slack_message_per_number_of_channels(num_of_channels, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_slack_channels
    mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.return_value = {"status_code": 200}

    channels = list()
    for i in range(num_of_channels):
        channels.append("channel")

    mock_reporting_notifications_NotificationManager._send_slack_channels(channels=channels, msg="halp")

    assert mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.call_count == num_of_channels


@pytest.mark.parametrize("returned_response", [302, 403, 500, Exception])
def test_raises_SlackSendError_on_bad_response_or_exception(returned_response, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_slack_channels
    mock_reporting_notifications_NotificationManager.slack_client.post_slack_message.return_value = {"status_code": returned_response}

    with pytest.raises(reporting.notifications.SlackSendError):
        mock_reporting_notifications_NotificationManager._send_slack_channels(channels=["channel"], msg="halp")