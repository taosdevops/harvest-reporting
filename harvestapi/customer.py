from typing import List
import re
import datetime

from harvest import Harvest
from harvest.harvestdataclasses import Client, TimeEntry

from reporting.config import Customer

import logging

logger = logging.getLogger(__name__)


def _get_current_month():  # Maybe move ??
    dm = datetime.datetime.today().month

    return f"{dm:02}"


def _get_current_year():  # Maybe move ??
    dm = datetime.datetime.today().year

    return f"{dm:04}"


class HarvestCustomer(object):
    def __init__(self, client: Harvest, config: Customer, customer: Client):
        self.client = client
        self.data = customer
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
