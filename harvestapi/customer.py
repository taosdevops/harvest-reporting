import datetime
import logging
import math
import re
from typing import List

from harvest import Harvest
from harvest.harvestdataclasses import Client, TimeEntry

from reporting.config import Customer, Recipients, ReporterConfig

LOGGER = logging.getLogger(__name__)


def _get_current_month():  # Maybe move ??
    dm = datetime.datetime.today().month

    return f"{dm:02}"


def _get_current_year():  # Maybe move ??
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
        self.time_entries = self._time_entries()

    def _time_entries(self) -> List[TimeEntry]:
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
        regex = re.compile("([0-9]{4})-([0-9]{2})-([0-9]{2})")

        return sum(
            [
                entry.hours
                for entry in self.time_entries
                if regex.search(entry.spent_date).group(2) == month
                and regex.search(entry.spent_date).group(1) == year
            ]
        )

    def time_remaining(
        self, month: str = _get_current_month(), year: str = _get_current_year(),
    ) -> float:
        regex = re.compile("([0-9]{4})-([0-9]{2})-([0-9]{2})")

        return self.config.hours - self.time_used()

    def percentage_hours_used(self) -> int:
        return int(math.ceil((self.time_used() / self.config.hours) * 100))


def get_recipients_from_config(customer: Client, config: ReporterConfig) -> Recipients:
    for config_customer in config.customers:
        if customer.name == config_customer.name:
            LOGGER.debug(
                f"Matched customer {customer.name} to recipients {config_customer.recipients}"
            )
            return config_customer.recipients
    return Recipients()
