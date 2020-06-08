import re
from unittest import TestCase
from unittest.mock import MagicMock

from reporting.utils import get_color_code_for_utilization, get_payload


class TestUtilsColorCode(TestCase):
    def setUp(self):
        self.client = {"hours_used": 60, "name": "DSC", "percent": 50, "hours_left": 30}

    def test_get_color_returns_red_for_over_100(self):
        self.assertEqual(get_color_code_for_utilization(101), "#ff0000")


class TestGetPayload(TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.percent = 50
        # {"hours_used": 60, "name": "DSC", "percent": 50, "hours_left": 30}

    def test_returns_slack_payload(self):
        payload_under_test = get_payload(self.client)
        pattern = "attachments"
        expectation = re.search(pattern, str(payload_under_test))
        self.assertTrue(expectation)

    def test_returns_teams_payload(self):
        payload_under_test = get_payload(self.client, _format="teams")
        pattern = "MessageCard"
        expectation = re.search(pattern, str(payload_under_test))
        self.assertTrue(expectation)

    def test_returns_raise_exeption(self):
        with self.assertRaises(Exception):
            get_payload(self.client, _format="expected failure")
