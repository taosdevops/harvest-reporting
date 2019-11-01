from unittest import TestCase
from hreporting.utils import get_color_code_for_utilization, get_payload
from taosdevopsutils.slack import Slack


class TestUtilsColorCode(TestCase):
    def test_get_color_returns_red_for_over_100(self):
        self.assertEqual(get_color_code_for_utilization(101), "#ff0000")


class TestGetPayload(TestCase):
    def test_returns_slack_payload(self):
        payload_under_test = get_payload(50, "SVB", 4, 5)
        expectation = "slack"
        self.assertEqual(payload_under_test, expectation)

    def test_returns_teams_payload(self):
        payload_under_test = get_payload(50, "SVB", 4, 5, _format="teams")
        expectation = "teams"
        self.assertEqual(payload_under_test, expectation)
