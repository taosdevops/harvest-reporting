#!/usr/bin/env python3
import re
import os
import json
import math
import fileinput
import urllib.request
from datetime import date
from datetime import time
from time import gmtime, strftime

DSC = 'client_id=8102048'

url = "https://api.harvestapp.com/v2/time_entries?client_id=8102048"
headers = {
    "User-Agent": "Python Harvest API Sample",
    "Authorization": "Bearer 1958933.pt.AQdIixLiVPwHPcd0qwPxL0qYh3bKGanbkPBm3yraWoDHA9BNReJODWQfeWnAQZDC9KBmEws1gwDOpVdJB4LIrw",
    "Harvest-Account-ID": "1121001"
}

request = urllib.request.Request(url=url, headers=headers)
response = urllib.request.urlopen(request, timeout=5)
responseBody = response.read().decode("utf-8")
jsonResponse = json.loads(responseBody)
timeEntries = jsonResponse["time_entries"]

regex = re.compile('([0-9]{4})-([0-9]{2})-([0-9]{2})')
today = date.today().strftime('%Y-%m-%d')
currentMonth = regex.search(today).group(2)

hours_used = 0.00
total_hours = 80.00

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

for items in timeEntries:
    m = regex.search(items["spent_date"]).group(2)
    if str(m) == str(currentMonth):
      #print(m)
        total = items["hours"]
        hours_used += total
        left = total_hours - hours_used

#used = strftime("%M:%S", gmtime(hours_used *60))
#left = strftime("%M:%S", gmtime(left *60))

print  ("DSC ", truncate(hours_used, 2),"/80 Hours Used\t", truncate(left, 2),"/80 Hours Remaining")
#print(used, "Hours Used")
#print (truncate(left, 2), "Hours Left")


