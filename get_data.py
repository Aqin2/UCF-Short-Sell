# get data for day, week, 3 month, etc

import get_market_data as gmd
import get_market_data_polygon as gmd_polygon
from datetime import datetime, timedelta
import pandas_market_calendars as mcal

FILE_NAME = "blue_orca.txt"

def get_exchange_calendar(exchange_code):
    """Get the appropriate market calendar for the given exchange"""
    exchange_map = {
        # North America
        'NYSE': 'NYSE',            # New York Stock Exchange
        'NASDAQ': 'NASDAQ',        # NASDAQ
        'TSX': 'TSX',             # Toronto Stock Exchange
        'TSXV': 'TSX',            # TSX Venture Exchange
        'AMEX': 'NYSE',           # American Stock Exchange (now NYSE American)
        
        # Europe
        'LSE': 'LSE',             # London Stock Exchange
        'ETR': 'XETRA',           # Deutsche Börse XETRA (Frankfurt)
        'XTRA': 'XETRA',          # XETRA (alternate code)
        'FRA': 'FWB',             # Frankfurt Stock Exchange
        'EPA': 'EURONEXT',        # Euronext Paris
        'AMS': 'EURONEXT',        # Euronext Amsterdam
        'BRU': 'EURONEXT',        # Euronext Brussels
        'SWX': 'SIX',             # Swiss Exchange
        'STO': 'NASDAQ',          # Stockholm Stock Exchange (Nasdaq Nordic)
        'CPH': 'NASDAQ',          # Copenhagen Stock Exchange
        'HEL': 'NASDAQ',          # Helsinki Stock Exchange
        'OSL': 'OSLO',            # Oslo Stock Exchange
        'WSE': 'WSE',             # Warsaw Stock Exchange
        'MIL': 'MTA',             # Borsa Italiana (Milan)
        'MCE': 'BME',             # Madrid Stock Exchange
        'ELI': 'EURONEXT',        # Euronext Lisbon
        
        # Asia-Pacific
        'TYO': 'JPX',             # Tokyo Stock Exchange
        'TSE': 'JPX',             # Tokyo Stock Exchange (alternate)
        'JPX': 'JPX',             # Japan Exchange Group
        'HKG': 'HKEX',            # Hong Kong Stock Exchange
        'HK': 'HKEX',             # Hong Kong (alternate)
        'HKEX': 'HKEX',           # Hong Kong Exchange (alternate)
        'SS': 'SSE',              # Shanghai Stock Exchange
        'SHH': 'SSE',             # Shanghai (alternate)
        'SZ': 'SZSE',             # Shenzhen Stock Exchange
        'SHZ': 'SZSE',            # Shenzhen (alternate)
        'ASX': 'ASX',             # Australian Securities Exchange
        'ASXL': 'ASX',            # ASX (alternate)
        'NZE': 'NZX',             # New Zealand Stock Exchange
        'KRX': 'KRX',             # Korea Exchange
        'KOS': 'KRX',             # Korea Stock Exchange
        'BSE': 'BSE',             # Bombay Stock Exchange
        'NSE': 'NSE',             # National Stock Exchange of India
        'SGX': 'SGX',             # Singapore Exchange
        'SET': 'SET',             # Stock Exchange of Thailand
        'IDX': 'IDX',             # Indonesia Stock Exchange
        'MYX': 'MYX',             # Bursa Malaysia
        
        # Middle East & Africa
        'JSE': 'JSE',             # Johannesburg Stock Exchange
        'TASE': 'TASE',           # Tel Aviv Stock Exchange
        'ADX': 'ADX',             # Abu Dhabi Securities Exchange
        'DFM': 'DFM',             # Dubai Financial Market
        'SAU': 'TADAWUL',         # Saudi Stock Exchange (Tadawul)
        
        # South America
        'BVMF': 'BMFBOVESPA',     # B3 (Brazil Stock Exchange)
        'BMV': 'BMV',             # Mexican Stock Exchange
        'BCS': 'BCS',             # Santiago Stock Exchange
        'BCBA': 'BCBA'            # Buenos Aires Stock Exchange
    }
    calendar_name = exchange_map.get(exchange_code, 'NYSE')  # Default to NYSE if exchange not found
    return mcal.get_calendar(calendar_name)

def parse_date(date_str):
    """Parse date string to datetime object"""
    if '/' in date_str:
        return datetime.strptime(date_str, '%m/%d/%Y')
    return datetime.strptime(date_str, '%Y-%m-%d')

def get_next_business_day(date_str, exchange_code='NYSE'):
    """Get the next business day after the given date, accounting for market holidays"""
    date = parse_date(date_str)
    calendar = get_exchange_calendar(exchange_code)
    
    # Get the next trading day
    schedule = calendar.schedule(start_date=date, end_date=date + timedelta(days=10))
    trading_days = schedule.index.date
    
    # Find the next trading day after our date
    for trading_day in trading_days:
        if trading_day > date.date():
            return trading_day.strftime('%Y-%m-%d')
    
    return None

def get_future_business_day(date_str, days, exchange_code='NYSE'):
    """Get a future business day that's approximately the specified number of calendar days ahead"""
    date = parse_date(date_str)
    calendar = get_exchange_calendar(exchange_code)
    
    # Get schedule for a wider range to ensure we capture enough trading days
    schedule = calendar.schedule(
        start_date=date,
        end_date=date + timedelta(days=days + 20)  # Add buffer for holidays
    )
    trading_days = schedule.index.date
    
    # Find the trading day closest to our target date
    target_date = date + timedelta(days=days)
    closest_day = min(trading_days, key=lambda x: abs((x - target_date.date()).days))
    
    # If the closest day is before our target, try to get the next trading day
    if closest_day < target_date.date() and len(trading_days) > list(trading_days).index(closest_day) + 1:
        closest_day = list(trading_days)[list(trading_days).index(closest_day) + 1]
    
    return closest_day.strftime('%Y-%m-%d')

f = open(FILE_NAME, "r")
o = open(FILE_NAME + ".out", "w")

import re

def get_market_data_robust(a, b, c):
    result = gmd.get_stock_price(a, b, c)
    if result:
        return result
    else:
        return gmd_polygon.get_stock_price(a, b, c)

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
    result = get_market_data_robust(data[1], data[0], data[2])
    
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
        next_day = get_next_business_day(data[2], data[0])
        next_day_result = get_market_data_robust(data[1], data[0], next_day)
        if next_day_result:
            prices[2] = next_day_result['open']
            prices[3] = next_day_result['close']
        
        # Get one week data
        one_week = get_future_business_day(data[2], 7, data[0])
        week_result = get_market_data_robust(data[1], data[0], one_week)
        if week_result:
            prices[4] = week_result['open']
            prices[5] = week_result['close']
        
        # Get one month data
        one_month = get_future_business_day(data[2], 30, data[0])
        month_result = get_market_data_robust(data[1], data[0], one_month)
        if month_result:
            prices[6] = month_result['open']
            prices[7] = month_result['close']
        
        # Get three month data
        three_month = get_future_business_day(data[2], 90, data[0])
        three_month_result = get_market_data_robust(data[1], data[0], three_month)
        if three_month_result:
            prices[8] = three_month_result['open']
            prices[9] = three_month_result['close']
        
        # Get six month data
        six_month = get_future_business_day(data[2], 180, data[0])
        six_month_result = get_market_data_robust(data[1], data[0], six_month)
        if six_month_result:
            prices[10] = six_month_result['open']
            prices[11] = six_month_result['close']

    # Print all prices as comma-separated values
    print(f"{data[0]},{data[1]},{data[2]},{','.join(str(p) for p in prices)}", file=o)