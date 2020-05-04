import datetime
import re
from typing import List

import requests


def _get_current_month():  # Maybe move ??
    dm = datetime.datetime.today().month

    return f"{dm:02}"

def _get_current_year():  # Maybe move ??
    dm = datetime.datetime.today().year

    return f"{dm:04}"


class HarvestClient:
    """ Harvest Client """

    _base_url = "https://api.harvestapp.com/v2/"
    _client_endpoint = "clients"
    _client_time_endpoint = "time_entries?client_id="

    def __init__(self, bearer_token: str, account_id: str, config=None):
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Harvest-Account-ID": account_id,
        }
        self.config = config or {}

    def _get_client_config(self, client_name: str):
        try:
            return [
                client_entry

                for client_entry in self.config.get("clients", [])

                if client_entry["name"] == client_name
            ][0]
        except IndexError:
            return {}

    def list_clients(self) -> List[dict]:
        """ Returns array of harvest Clients"""
        uri = self._base_url + self._client_endpoint
        response = requests.get(uri, headers=self.headers)
        json_response = response.json()
        clients = json_response["clients"]

        return clients

    def get_client_by_id(self, client_id: str) -> list:
        """ Returns array of harvest Clients"""
        uri = self._base_url + self._client_endpoint + f"/{client_id}"
        response = requests.get(uri, headers=self.headers)
        json_response = response.json()

        return json_response

    def get_client_time(self, client_id: str) -> List[dict]:
        """ Returns Time entries for Harvest Clients """
        uri = self._base_url + self._client_time_endpoint + str(client_id)
        response = requests.get(uri, headers=self.headers)
        json_response = response.json()

        entries = json_response["time_entries"]

        while json_response.get("links", {}).get("next"):
            # Make follow up calls to compile the pages
            response = requests.get(
                json_response["links"]["next"], headers=self.headers
            )
            json_response = response.json()
            entries.extend(json_response["time_entries"])

        return entries

    def get_client_time_used(
        self, client_id: str,
        month: str = _get_current_month(),
        year: str  = _get_current_year(),
    ) -> float:
        """ returns sum of client time used for the given month """
        regex = re.compile("([0-9]{4})-([0-9]{2})-([0-9]{2})")

        return sum(
            [
                item["hours"]

                for item in self.get_client_time(client_id)

                if regex.search(item["spent_date"]).group(2) == month and
                   regex.search(item["spent_date"]).group(1) == year
            ]
        )

    def get_client_time_allotment(self, client_name: str) -> float:
        """ returns client allotment provided in class.config. *default=60* """
        client_config = self._get_client_config(client_name)

        return client_config.get("hours", self.config.get("default_hours", 80))

    def get_exception_hook(self) -> str:
        return self.config.get("exceptionHook", "")

    def get_client_hooks(self, client_name) -> List[str]:
        """ Returns list of webhooks and emails registered for client. """
        client_config = self._get_client_config(client_name)

        return {
            "hooks": [
                *client_config.get("hooks", []),
                *self.config.get("globalHooks", []),
            ],
            "emails": [
                *client_config.get("emails", []),
                *self.config.get("globalEmails", []),
            ],
        }
