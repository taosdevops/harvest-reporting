import re
from unittest import TestCase
from unittest.mock import MagicMock

from vcr_unittest import VCRTestCase

from hreporting.client import HarvestClient
from hreporting.notifications import NotificationManager
from hreporting.utils import get_color_code_for_utilization, get_payload


class TestExceptionChannel(VCRTestCase):
    def setUp(self):
        self.client = HarvestClient(
            hoursUsed=60,
            hoursLeft=40,
            hoursTotal=100,
            name="DSC",
            percent=50,
            clientId="TestingId",
            templateId=None,
            hooks=[],
        )
        self.clients = [self.client]
        self.from_email = "DevOpsNow@test.com"

        self.SLACK_CLIENT = MagicMock()
        self.exception = MagicMock()
        self.webhook_url = MagicMock()
        self.harvest_client = MagicMock()
        self.harvest_client.get_client_time_allotment = MagicMock(return_value=30)
        self.harvest_client.get_client_time_used = MagicMock(return_value=15)

        self.notifier = NotificationManager(
            fromEmail=self.from_email,
            exceptionHooks=self.exception,
            clients=self.clients,
            harvestClient=self.harvest_client,
        )

    def test_returns_channel_post(self):
        channel_post_under_test = self.notifier.channel_post(
            webhook_url="https://outlook.office.com/", client=self.client
        )
        pattern = "MessageCard"
        expectation = re.search(pattern, str(channel_post_under_test))
        self.assertTrue(expectation)

    def test_exception_channel_post(self):
        """ Verification that a throw will cause an error """

        with self.assertRaises(Exception):
            self.notifier.channel_post(
                webhook_url="https://outlook.office.com/", client=None
            )
