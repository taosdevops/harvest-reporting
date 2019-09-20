from unittest import TestCase
from hreporting.utils import get_color_code_for_utilization


class TestUtilsColorCode(TestCase):
    def test_get_color_returns_red_for_over_100(self):
        self.assertEqual(get_color_code_for_utilization(101), "#ff0000")
