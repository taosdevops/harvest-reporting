#!/usr/bin/env python3
import re
import os
import json
import math
import fileinput
import requests
import urllib.request
from datetime import date
from datetime import time



# Build headers
headers = {
    'Authorization': 'Bearer 1958933.pt.AQdIixLiVPwHPcd0qwPxL0qYh3bKGanbkPBm3yraWoDHA9BNReJODWQfeWnAQZDC9KBmEws1gwDOpVdJB4LIrw',
    'Harvest-Account-ID': '1121001'
}

# Define uri's
api = 'https://api.harvestapp.com/v2/'
clientUri = 'clients'
timeEntriesUri = 'time_entries?client_id=' 

# Build url to get clients
getClient = api+clientUri

# Get client name and id
clientRequest = urllib.request.Request(url=getClient, headers=headers)
clientResponse = urllib.request.urlopen(clientRequest, timeout=5)
responseBody = clientResponse.read().decode('utf-8')
jsonResponse = json.loads(responseBody)
clientList = jsonResponse['clients']

for client in clientList:
    clientId = client['id']
    clientName = client['name']
    clientActive = client['is_active']
    if clientActive == True:
   
       # Build url to get time
       getTime = str(api) + str(timeEntriesUri) + str(clientId)

       # Get client time entries
       timeRequest = urllib.request.Request(url=getTime, headers=headers)
       timeResponse = urllib.request.urlopen(timeRequest, timeout=5)
       responseBody = timeResponse.read().decode('utf-8')
       jsonResponse = json.loads(responseBody)
       timeEntries = jsonResponse['time_entries']

       # Define regex pattern based on todays date, match month
       regex = re.compile('([0-9]{4})-([0-9]{2})-([0-9]{2})')
       today = date.today().strftime('%Y-%m-%d')
       currentMonth = regex.search(today).group(2)
    
       # Define hours
       hours_used = 0.00
       total_hours = 80.00
   
       # Get time entries based on regex month match
       for item in timeEntries:
           m = regex.search(item['spent_date']).group(2)
           if str(m) == str(currentMonth):
              total = item['hours']
              hours_used += total
       hours_left = total_hours - hours_used
    
       # Define decimal place to truncate
       def truncate(n, decimals=0):
           multiplier = 10 ** decimals
           return int(n * multiplier) / multiplier

       # Only keep 2 decimal places
       used = truncate(hours_used, 2)
       left = truncate(hours_left, 2)
           
       green  = '#49E20E'
       yellow = '#FFA812'
       orange = '#FF3300'
       red    = '#FF0000'
       black  = '#0F0F0F'
         
       regGreen  = re.compile('^[0-9].[0-9][0-9]|[1-4][0-9].[0-9][0-9]')
       regYellow = re.compile('5[0-9].[0-9][0-9]')
       regOrange = re.compile('6[0-9].[0-9][0-9]')
       regRed    = re.compile('7[0-9].[0-9][0-9]')
       regBlack  = re.compile('[8-9][0-9].[0-9][0-9]|[1-3][0-9][0-9].[0-9][0-9]')
       
       colors = (regGreen,regYellow,regOrange,regRed,regBlack)
       
       for reg in colors:
           match = reg.search(str(left))
           if str(match) == str(regGreen):
              color = green
           elif str(match) == str(regYellow):
              color = yellow
           elif str(match) == str(regOrange):
              color = orange
           elif str(match) == str(regRed):
              color = red
           else:
               str(match) == str(regBlack)
               color = black

#       # Post to slack
#       webhook_url = '***REMOVED***'
#       slack_data = { 
#           "attachments": [
#               {
#                   "color": color,
#                   "text": clientName,
#                   "fields": [
#                        {
#                            "title": "Hours Used",
#                            "value": used,
#                            "short": "true"
#                        },    
#                        {
#                            "title": "Hours Remaining",
#                            "value": left,
#                            "short": "true"
#                        }    
#                   ]
#               }
#           ]
#       }
#    
#    response = requests.post(
#    webhook_url, data=json.dumps(slack_data),
#    headers={'Content-Type': 'application/json'}
#    )
#    print('Response: ' + str(response.text))
#    print('Response code: ' + str(response.status_code))
#
    Hour_Report_Template = '''
    Client:           {clientName}
    Used Hours:       {used}
    Remaining Hours:  {left}
    Color:            {color}
    '''
    print (str.format(
    Hour_Report_Template,
    clientName = clientName,
    used       = used,
    left       = left,
    color      = color,
    ))
