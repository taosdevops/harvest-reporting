import datetime
import logging
import math
import re
from typing import List

from harvest.harvest import Harvest
from harvest.harvestdataclasses import Client, TimeEntry

from reporting.config import Customer, Recipients, ReporterConfig

LOGGER = logging.getLogger(__name__)


def _get_current_month() -> str:
    """Get the month field from the execution time of this function.

    Returns:
        str: Month number in string form
    """
    dm = datetime.datetime.today().month

    return f"{dm:02}"


def _get_current_year() -> str:
    """Get the year field from the execution time of this function.

    Returns:
        str: year number in string form
    """
    dm = datetime.datetime.today().year

    return f"{dm:04}"


class HarvestCustomer(object):
    def __init__(
        self,
        client: Harvest,
        config: Customer,
        recipients: Recipients,
        customer: Client,
    ):
        self.client = client
        self.config = config
        self.data = customer
        self.recipients = recipients
        self._time_entries = None

    @property
    def time_entries(self) -> List[TimeEntry]:
        """Class property that stores a customer's time entries. Values are all
        lazy loaded.

        Returns:
            List[TimeEntry]: Time entry data as fetched from the Harvest API
        """
        if self._time_entries == None:
            self._time_entries = self._get_time_entries()
        return self._time_entries

    def _get_time_entries(self) -> List[TimeEntry]:
        """Helper function to fetch time entries from Harvest API

        Returns:
            List[TimeEntry]: Time entry data as fetched from the Harvest API
        """
        page = 1
        te = []
        while page:
            entries = self.client.time_entries(
                client_id=self.data.id, page=page
            ).time_entries
            if len(entries) == 0:
                break
            te += entries
            page += 1

        return te

    def time_used(
        self, month: str = _get_current_month(), year: str = _get_current_year(),
    ) -> float:
        """Returns the amount of time used by a customer in the specified
        month/year.

        Args:
            month (str, optional): Month number for which to calculate. Defaults to _get_current_month().
            year (str, optional): Year number for which to calculate. Defaults to _get_current_year().

        Returns:
            float: Total utilized time rounded to the nearest tenth
        """
        regex = re.compile("([0-9]{4})-([0-9]{2})-([0-9]{2})")

        return round(sum(
            [
                entry.hours
                for entry in self.time_entries
                if regex.search(entry.spent_date).group(2) == month
                and regex.search(entry.spent_date).group(1) == year
            ]
        ), 1)

    def time_remaining(
        self, month: str = _get_current_month(), year: str = _get_current_year(),
    ) -> float:
        """Calculates a customer's remaining time for the specified month/year.

        Args:
            month (str, optional): Month for which to calculate. Defaults to _get_current_month().
            year (str, optional): Year for which to calculate. Defaults to _get_current_year().

        Returns:
            float: Time remaining rounded to the nearest tenth
        """
        return round((self.config.hours - self.time_used(month=month, year=year)), 1)

    def percentage_hours_used(
        self, month: str = _get_current_month(), year: str = _get_current_year()
    ) -> float:
        """Percentage of a customer's allotted hours utilized for the given month/year.

        Args:
            month (str, optional): Month for which to calculate. Defaults to _get_current_month().
            year (str, optional): Year for which to calculate. Defaults to _get_current_year().

        Returns:
            float: Percentage of hours used rounded to the nearest tenth
        """
        return round(((self.time_used(month=month, year=year) / self.config.hours) * 100), 1)


def get_recipients_from_config(customer: Client, config: ReporterConfig) -> Recipients:
    """Helper function to match a customer to the recipients specified in the config.

    Args:
        customer (Client): Customer to fetch recipients for
        config (ReporterConfig): Config specifying the customer-to-recipient mapping

    Returns:
        Recipients: Recipients object defining which channels and people things should be sent to.
    """
    for config_customer in config.customers:
        if customer.name == config_customer.name:
            LOGGER.debug(
                f"Matched customer {customer.name} to recipients {config_customer.recipients}"
            )
            return config_customer.recipients
    return Recipients()
