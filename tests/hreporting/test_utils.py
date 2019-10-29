from unittest import TestCase
from hreporting.utils import get_color_code_for_utilization, get_payload
from taosdevopsutils.slack import Slack


class TestUtilsColorCode(TestCase):
    def test_get_color_returns_red_for_over_100(self):
        self.assertEqual(get_color_code_for_utilization(101), "#ff0000")


class TestGetPayload(TestCase):
    def test_returns_slack_payload(self):
        hook = "https://hooks.slack.com/webhook/blah/blah"
        slack_payload_expectation = hook.startswith("https://hooks.slack.com")
        self.assertEqual(get_payload(slack_payload_expectation)

    def test_returns_teams_payload(self):
        hook = "https://outlook.office.com/webhook/blah/blah"
        teams_payload_expectation = hook.startswith("https://outlook.office.com")
        self.assertEqual(get_payload(teams_payload_expectation)
