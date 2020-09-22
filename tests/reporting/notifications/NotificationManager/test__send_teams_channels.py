from unittest.mock import MagicMock, patch
import pytest

import reporting.notifications


@pytest.mark.parametrize("num_of_channels", [0, 1, 2])
@patch("reporting.notifications.pymsteams")
def test_assert_call_count_of_pymsteams_connector_card_send_per_number_of_channels(mock_pymsteams, num_of_channels, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_teams_channels
    mock_pymsteams.connectorcard.return_value.send.return_value = True

    channels = list()
    for i in range(num_of_channels):
        channels.append("channel")

    mock_reporting_notifications_NotificationManager._send_teams_channels(channels=channels, msg="halp")

    assert mock_pymsteams.connectorcard.return_value.send.call_count == num_of_channels


@pytest.mark.parametrize("send_return_value", [False, Exception])
@patch("reporting.notifications.pymsteams")
def test_bad_pymsteams_response_raises_TeamsSendError(mock_pymsteams, send_return_value, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_teams_channels
    mock_pymsteams.connectorcard.return_value.send.side_effect = send_return_value

    with pytest.raises(reporting.notifications.TeamsSendError):
        mock_reporting_notifications_NotificationManager._send_teams_channels(channels=["channel"], msg="halp")