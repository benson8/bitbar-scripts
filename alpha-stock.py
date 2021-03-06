#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# <bitbar.title>Alpha Vantage Stock Ticker</bitbar.title>
# <bitbar.version>0.1</bitbar.version>
# <bitbar.author>Ben Rogers</bitbar.author>
# <bitbar.author.github>benson8</bitbar.author.github>
# <bitbar.desc>Provides a rotating stock ticker in your menu bar</bitbar.desc>
# <bitbar.dependencies>python</bitbar.dependencies>
#
# requires installing 'holidays' package (`easy_install holidays` in my case)
#

from urllib.request import urlopen
#import urllib2
import json
import time
from datetime import date, timedelta, time
from datetime import datetime as dt
import decimal
import os
import sys
from pprint import pprint

import holidays

# support for touching a file
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

if not os.path.isfile('/tmp/stock.txt'):
   touch('/tmp/stock.txt')

# if on the weekend, reset to Friday for calculations
dayOfTheWeek = date.today().weekday()
yesterday = date.today() - timedelta(1)

if dayOfTheWeek == 6:
   today = date.today() - timedelta(2)
   yesterday = date.today() - timedelta(3)
elif dayOfTheWeek == 5:
   today = date.today() - timedelta(1)
   yesterday = date.today() - timedelta(2)
elif dayOfTheWeek == 0:
   today = date.today()
   yesterday = date.today() - timedelta(3)
else:
   today = date.today()

yesterdayString = str(yesterday)

# if a stock market holiday, reset yesterday appropriately
us_holidays = holidays.US()
holidayName = us_holidays.get(yesterdayString)
if holidayName:
  yesterday = date.today() - timedelta(4)
  yesterdayString = str(yesterday)

### REPLACE THESE VALUES
stocks="STOCK_SYMBOL"
apiKey="APIKEY"
###

now = dt.now()
nowTime = now.time()
if nowTime <= time(8,30):
   color = "gray"
   stockFile = open("/tmp/stock.txt", "r")
   yesterdayPrice = 0.00
   for line in stockFile:
      if yesterdayString in line:
         price = line.split(':')
         yesterdayPrice = round(float(price[1]), 2)
         foundYesterdaysPrice = True
   stockFile.close()
   priceChange = 0.00
   print("{} ${:,.2f} {:+.2f} | color={}".format(
        stocks, yesterdayPrice, priceChange, color
   ))
   sys.exit(0)

# Currently only supports one stock
query = ""
for i in stocks:
    query = i + "," + query

# daily url gives us yesterday's price
dailyUrl = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=compact&apikey={}".format(stocks, apiKey)
# batch url gives us current price
batchUrl = "https://www.alphavantage.co/query?function=BATCH_STOCK_QUOTES&symbols={}&apikey={}".format(stocks, apiKey)

readFromCache = False
try:
   u = urlopen(batchUrl)
except HTTPError as err:
   if err.code == 503:
      readFromCache = True
   else:
      raise

apiDown = False
if readFromCache == False: 
   query = u.read()
   lastResponse = open("/tmp/lastprice.json", "w")
   lastResponse.write(str(query))
   lastResponse.close()
else:
   responseCache = open("/tmp/lastprice.json", "r")
   query = responseCache.read()
   apiDown = True

batchJson = json.loads(query)

currentPrice = round(float(batchJson['Stock Quotes'][0]['2. price']), 2)

foundYesterdaysPrice = False
stockFile = open("/tmp/stock.txt", "r")
for line in stockFile:
   if yesterdayString in line:
      price = line.split(':')
      yesterdayPrice = round(float(price[1]), 2)
      foundYesterdaysPrice = True

stockFile.close()

# make only one call to dailyUrl every day, since it is slow
if foundYesterdaysPrice == False:
   y = urlopen(dailyUrl)
   query = y.read()
   dailyJson = json.loads(query)
   closePrice = round(float(dailyJson['Time Series (Daily)'][yesterdayString]['4. close']), 2)
   with open('/tmp/stock.txt', 'a') as stock_txt:
      stock_txt.write("{}: {:,.2f}\n".format(yesterdayString, closePrice))
      stock_txt.close()

foundOpenPrice = False

priceChange = currentPrice - yesterdayPrice

if apiDown == False: 
   color = "red" if priceChange < 0 else "green"
else:
   color = "gray"

print("{} ${:,.2f} {:+.2f} | color={}".format(
     stocks, currentPrice, priceChange, color
))

