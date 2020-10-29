from unittest.mock import MagicMock, patch

import pytest

import reporting.notifications


@pytest.mark.parametrize("num_of_channels", [0, 1, 2])
def test_assert_call_count_of_publish_to_pubsub_per_number_of_channels(num_of_channels, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_slack_channels
    del reporting.notifications.publish_to_pubsub
    reporting.notifications.publish_to_pubsub = MagicMock()

    channels = list()
    for i in range(num_of_channels):
        channels.append("channel")

    mock_reporting_notifications_NotificationManager._send_slack_channels(channels=channels, msg={"text": "halp"})

    assert reporting.notifications.publish_to_pubsub.call_count == num_of_channels


@pytest.mark.parametrize("mock_channel,mock_expected_payload,mock_expected_attributes", [
    ("Cinderella", {"channel": "Cinderella", "text": "halp"}, {"slack_api_method": "chat.postMessage"}), 
    ("https://hooks.slack.com", {"text": "halp"}, {"incoming_webhook_url": "https://hooks.slack.com"})
    ])
def test_assert_channel_parse_passes_params(mock_channel, mock_expected_payload, mock_expected_attributes, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_slack_channels
    del reporting.notifications.publish_to_pubsub
    reporting.notifications.publish_to_pubsub = MagicMock()

    channels = [mock_channel]

    mock_reporting_notifications_NotificationManager._send_slack_channels(channels=channels, msg={"text": "halp"})

    reporting.notifications.publish_to_pubsub.assert_called_with(project_id="dev-ops-now", topic_id="genericslackbot", payload=mock_expected_payload, attributes=mock_expected_attributes)
