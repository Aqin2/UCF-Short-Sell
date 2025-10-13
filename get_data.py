# get data for day, week, 3 month, etc

import get_market_data as gmd
from datetime import datetime, timedelta

FILE_NAME = "blue_orca.txt"

def get_next_business_day(date_str):
    """Get the next business day after the given date"""
    if '/' in date_str:
        date = datetime.strptime(date_str, '%m/%d/%Y')
    else:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    
    next_day = date + timedelta(days=1)
    # If it's Saturday or Sunday, move to Monday
    while next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        next_day += timedelta(days=1)
    return next_day.strftime('%Y-%m-%d')

def get_future_business_day(date_str, days):
    """Get a future business day that's approximately the specified number of calendar days ahead"""
    if '/' in date_str:
        date = datetime.strptime(date_str, '%m/%d/%Y')
    else:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    
    target_date = date + timedelta(days=days)
    # If it's Saturday or Sunday, move to next Monday
    while target_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        target_date += timedelta(days=1)
    return target_date.strftime('%Y-%m-%d')

f = open(FILE_NAME, "r")
o = open(FILE_NAME + ".out", "w")

import re

print(f"Exchange,Ticker,Publish_Date,Publish_Date_Open,Publish_Date_Close,"
      +"Next_Day_Open,Next_Day_Close,"
      +"One_Week_Open,One_Week_Close,"
      +"One_Month_Open,One_Month_Close,"
      +"Three_Month_Open,Three_Month_Close,"
      +"Six_Month_Open,Six_Month_Close",
    file=o)

for line in f.readlines()[1:]:
    data = re.findall(r'[\w/]+', line)
    print(data)
    
    # Get publish date data
    result = gmd.get_stock_price(data[1], data[0], data[2])
    
    prices = [
        None, # open price, publish date
        None, # close price, publish date
        None, # next day open
        None, # next day close
        None, # one week open
        None, # one week close
        None, # one month open
        None, # one month close
        None, # three month open
        None, # three month close
        None, # six month open
        None, # six month close
    ]

    if result:
        prices[0] = result['open']
        prices[1] = result['close']
        
        # Get next business day data
        next_day = get_next_business_day(data[2])
        next_day_result = gmd.get_stock_price(data[1], data[0], next_day)
        if next_day_result:
            prices[2] = next_day_result['open']
            prices[3] = next_day_result['close']
        
        # Get one week data
        one_week = get_future_business_day(data[2], 7)
        week_result = gmd.get_stock_price(data[1], data[0], one_week)
        if week_result:
            prices[4] = week_result['open']
            prices[5] = week_result['close']
        
        # Get one month data
        one_month = get_future_business_day(data[2], 30)
        month_result = gmd.get_stock_price(data[1], data[0], one_month)
        if month_result:
            prices[6] = month_result['open']
            prices[7] = month_result['close']
        
        # Get three month data
        three_month = get_future_business_day(data[2], 90)
        three_month_result = gmd.get_stock_price(data[1], data[0], three_month)
        if three_month_result:
            prices[8] = three_month_result['open']
            prices[9] = three_month_result['close']
        
        # Get six month data
        six_month = get_future_business_day(data[2], 180)
        six_month_result = gmd.get_stock_price(data[1], data[0], six_month)
        if six_month_result:
            prices[10] = six_month_result['open']
            prices[11] = six_month_result['close']

    # Print all prices as comma-separated values
    print(f"{data[0]},{data[1]},{data[2]},{','.join(str(p) for p in prices)}", file=o)