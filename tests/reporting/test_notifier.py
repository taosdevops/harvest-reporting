import re
from unittest import TestCase
from unittest.mock import MagicMock

from vcr_unittest import VCRTestCase

from harvestapi.client import HarvestCustomer
from reporting.notifications import NotificationManager
from reporting.utils import get_color_code_for_utilization, get_payload


class TestExceptionChannel(VCRTestCase):
    def setUp(self):
        self.client = {
            "hoursUsed": 60,
            "hoursLeft": 40,
            "hoursTotal": 100,
            "name": "DSC",
            "percent": 50,
            "id": "TestingId",
            "templateId": None,
            "hooks": [],
        }

        self.clients = [self.client]
        self.from_email = "DevOpsNow@test.com"

        self.SLACK_CLIENT = MagicMock()
        self.exception = MagicMock()
        self.webhook_url = MagicMock()
        self.harvestapi_client = MagicMock()
        self.harvestapi_client.get_client_time_allotment = MagicMock(return_value=30)
        self.harvestapi_client.get_client_time_used = MagicMock(return_value=15)

        self.notifier = NotificationManager(
            fromEmail=self.from_email,
            exceptionHooks=self.exception,
            clients=self.clients,
            harvestapi_client=self.harvestapi_client,
        )

    def test_returns_channel_post(self):
        channel_post_under_test = self.notifier.channel_post(
            webhook_url="https://outlook.office.com/", client=self.notifier.clients[0]
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
