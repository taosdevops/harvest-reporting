import re
import os
import json
import math
import fileinput
import urllib.request
import requests
import colorama
from colorama import Fore, Style
from datetime import date
from datetime import time
from hreporting.harvest_client import HarvestClient
from hreporting.utils import truncate, load_yaml, print_verify


bearer_token = "1958933.pt.AQdIixLiVPwHPcd0qwPxL0qYh3bKGanbkPBm3yraWoDHA9BNReJODWQfeWnAQZDC9KBmEws1gwDOpVdJB4LIrw"
harvest_account = "1121001"


def mainMethod():
    harvest_client = HarvestClient(
        bearer_token, harvest_account, load_yaml("config/clients.yaml")
    )

    active_clients = [
        client for client in harvest_client.list_clients() if client["is_active"]
    ]

    for client in active_clients:
        clientId = client["id"]
        clientName = client["name"]

        hours_used = harvest_client.get_client_time_used(clientId)
        total_hours = harvest_client.get_client_time_allotment(clientName)
        hours_left = total_hours - hours_used

        used = truncate(hours_used, 2)
        left = truncate(hours_left, 2)

        percent = used / total_hours * 100

        print_verify(used, clientName, percent, left)

        [
            slackPost(hook, used, clientName, percent, left)
            for hook in harvest_client.get_client_hooks(clientName)
        ]


if __name__ == "__main__":
    mainMethod()
