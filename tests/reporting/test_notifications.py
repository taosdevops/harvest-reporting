import re
from unittest import TestCase
from unittest.mock import MagicMock

from vcr_unittest import VCRTestCase

from harvestapi.customer import HarvestCustomer
from reporting.notifications import NotificationManager


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

    def test_get_color_returns_red_for_over_100(self):
        self.assertEqual(
            NotificationManager()._get_color_code_for_utilization(101), "#ff0000"
        )

    def test_returns_slack_payload(self):
        payload_under_test = NotificationManager(self.client)
        pattern = "attachments"
        expectation = re.search(pattern, str(payload_under_test))
        self.assertTrue(expectation)

    def test_returns_teams_payload(self):
        payload_under_test = NotificationManager()._get_payload(
            self.client, _format="teams"
        )
        pattern = "MessageCard"
        expectation = re.search(pattern, str(payload_under_test))
        self.assertTrue(expectation)

    def test_returns_raise_exeption(self):
        with self.assertRaises(Exception):
            NotificationManager()._get_payload(self.client, _format="expected failure")
