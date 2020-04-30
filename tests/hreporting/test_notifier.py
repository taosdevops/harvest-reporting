import re
from unittest import TestCase
from unittest.mock import MagicMock

from vcr_unittest import VCRTestCase

from hreporting.notifications import NotificationManager
from hreporting.utils import get_color_code_for_utilization, get_payload


class TestExceptionChannel(VCRTestCase):
    def setUp(self):
        self.from_email = "DevOpsNow@test.com"
        self.notifier = NotificationManager(self.from_email, None)
        self.SLACK_CLIENT = MagicMock()
        self.client = MagicMock()
        self.exception = MagicMock()
        self.webhook_url = MagicMock()

    def test_returns_channel_post(self):
        channel_post_under_test = self.notifier.channel_post(
            "https://outlook.office.com/", 60, "SVB", 50, 30
        )
        pattern = "MessageCard"
        expectation = re.search(pattern, str(channel_post_under_test))
        self.assertTrue(expectation)

    def test_exception_channel_post(self):
        """ Verification that a throw will cause an error """

        with self.assertRaises(Exception):
            self.notifier.channel_post(
                self.exception, self.client, self.webhook_url, None, None
            )
