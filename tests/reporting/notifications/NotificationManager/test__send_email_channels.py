from unittest.mock import MagicMock, patch
import pytest

import reporting.notifications


@patch("reporting.notifications.SendGridSummaryEmail")
def test_successful_response(mock_sendgridsummaryemail, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_email_channels

    mock_sendgridsummaryemail.return_value.send.return_value.status_code = 299

    channels = ["channel"]

    mock_reporting_notifications_NotificationManager._send_email_channels(channels=channels, msg="halp")

    mock_sendgridsummaryemail.return_value.send.assert_called_once()


@pytest.mark.parametrize("returned_response", [302, 403, 500])
@patch("reporting.notifications.SendGridSummaryEmail")
def test_raises_EmailSendError_on_bad_response(mock_sendgridsummaryemail, returned_response, mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_email_channels
    mock_sendgridsummaryemail.return_value.send.return_value.status_code = returned_response

    with pytest.raises(reporting.notifications.EmailSendError):
        mock_reporting_notifications_NotificationManager._send_email_channels(channels=["channel"], msg="halp")


@patch("reporting.notifications.SendGridSummaryEmail")
def test_raises_EmailSendError_on_exception(mock_sendgridsummaryemail,  mock_reporting_notifications_NotificationManager):
    del mock_reporting_notifications_NotificationManager._send_email_channels
    mock_sendgridsummaryemail.return_value.send.side_effect = Exception

    with pytest.raises(reporting.notifications.EmailSendError):
        mock_reporting_notifications_NotificationManager._send_email_channels(channels=["channel"], msg="halp")
