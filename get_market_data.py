# pip install yfinance
import yfinance as yf
from datetime import datetime, timedelta

def get_stock_price(ticker, exchange, date_str):
    """
    Retrieve the opening and closing price for a stock on a specific date.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AYA')
        exchange (str): Exchange code (e.g., 'TSX', 'NYSE', 'NASDAQ')
        date_str (str): Date in format 'M/D/YYYY' or 'YYYY-MM-DD'
    
    Returns:
        dict: Dictionary containing 'open', 'close', 'date', and 'ticker' keys
              Returns None if data is not available
    
    Example:
        >>> result = get_stock_price('AYA', 'TSX', '9/25/2025')
        >>> print(result)
        {'ticker': 'AYA.TO', 'date': '2025-09-25', 'open': 10.50, 'close': 10.75}
    """
    
    # Exchange suffix mapping for yfinance
    exchange_suffixes = {
        # North America
        'TSX': '.TO',           # Toronto Stock Exchange
        'TSXV': '.V',           # TSX Venture Exchange
        'NYSE': '',             # New York Stock Exchange
        'NASDAQ': '',           # NASDAQ
        'AMEX': '',             # American Stock Exchange
        'OTCMKTS': '',          # OTC Markets
        'OTCQB': '',            # OTC QB
        'OTCQX': '',            # OTC QX
        
        # Europe
        'LSE': '.L',            # London Stock Exchange
        'ETR': '.DE',           # Deutsche Börse XETRA (Frankfurt)
        'XTRA': '.DE',          # XETRA (alternate code)
        'FRA': '.F',            # Frankfurt Stock Exchange
        'EPA': '.PA',           # Euronext Paris
        'AMS': '.AS',           # Euronext Amsterdam
        'BRU': '.BR',           # Euronext Brussels
        'SWX': '.SW',           # Swiss Exchange (SIX)
        'STO': '.ST',           # Stockholm Stock Exchange (Nasdaq Nordic)
        'CPH': '.CO',           # Copenhagen Stock Exchange
        'HEL': '.HE',           # Helsinki Stock Exchange
        'OSL': '.OL',           # Oslo Stock Exchange
        'WSE': '.WA',           # Warsaw Stock Exchange
        'MIL': '.MI',           # Borsa Italiana (Milan)
        'MCE': '.MC',           # Madrid Stock Exchange
        'ELI': '.LS',           # Euronext Lisbon
        
        # Asia-Pacific
        'TYO': '.T',            # Tokyo Stock Exchange
        'TSE': '.T',            # Tokyo Stock Exchange (alternate)
        'JPX': '.T',            # Japan Exchange Group
        'HKG': '.HK',           # Hong Kong Stock Exchange
        'HK': '.HK',            # Hong Kong (alternate)
        'HKEX': '.HK',          # Hong Kong Exchange (alternate)
        'SS': '.SS',            # Shanghai Stock Exchange
        'SHH': '.SS',           # Shanghai (alternate)
        'SZ': '.SZ',            # Shenzhen Stock Exchange
        'SHZ': '.SZ',           # Shenzhen (alternate)
        'ASX': '.AX',           # Australian Securities Exchange
        'ASXL': '.AX',          # ASX (alternate)
        'NZE': '.NZ',           # New Zealand Stock Exchange
        'KRX': '.KS',           # Korea Exchange (Seoul)
        'KOS': '.KS',           # Korea Stock Exchange
        'BSE': '.BO',           # Bombay Stock Exchange
        'NSE': '.NS',           # National Stock Exchange of India
        'SGX': '.SI',           # Singapore Exchange
        'SET': '.BK',           # Stock Exchange of Thailand
        'IDX': '.JK',           # Indonesia Stock Exchange
        'MYX': '.KL',           # Bursa Malaysia
        
        # Middle East & Africa
        'JSE': '.JO',           # Johannesburg Stock Exchange
        'TASE': '.TA',          # Tel Aviv Stock Exchange
        'ADX': '.AD',           # Abu Dhabi Securities Exchange
        'DFM': '.DU',           # Dubai Financial Market
        'SAU': '.SAU',          # Saudi Stock Exchange (Tadawul)
        
        # South America
        'BVMF': '.SA',          # B3 (Brazil Stock Exchange)
        'BMV': '.MX',           # Mexican Stock Exchange
        'BCS': '.SN',           # Santiago Stock Exchange
        'BCBA': '.BA',          # Buenos Aires Stock Exchange
    }
    
    # Get the appropriate suffix
    suffix = exchange_suffixes.get(exchange.upper(), '')
    full_ticker = f"{ticker}{suffix}"
    
    # Parse the date
    try:
        if '/' in date_str:
            target_date = datetime.strptime(date_str, '%m/%d/%Y')
        else:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format. Use 'M/D/YYYY' or 'YYYY-MM-DD'")
        return None
    
    # Fetch data for the target date (plus a buffer for weekends/holidays)
    start_date = target_date - timedelta(days=7)
    end_date = target_date + timedelta(days=1)
    
    try:
        # Download stock data
        stock = yf.Ticker(full_ticker)
        df = stock.history(start=start_date.strftime('%Y-%m-%d'), 
                          end=end_date.strftime('%Y-%m-%d'))
        
        if df.empty:
            print(f"No data available for {full_ticker}")
            return None
        
        # Find the exact date or closest trading day
        target_date_str = target_date.strftime('%Y-%m-%d')
        df.index = df.index.tz_localize(None)  # Remove timezone for comparison
        
        # Try to get exact date
        matching_rows = df[df.index.strftime('%Y-%m-%d') == target_date_str]
        
        if matching_rows.empty:
            print(f"No trading data on {target_date_str}. Market may have been closed.")
            print(f"Available dates: {df.index.strftime('%Y-%m-%d').tolist()}")
            return None
        
        row = matching_rows.iloc[0]
        
        result = {
            'ticker': full_ticker,
            'date': target_date_str,
            'open': round(float(row['Open']), 2),
            'close': round(float(row['Close']), 2),
            'high': round(float(row['High']), 2),
            'low': round(float(row['Low']), 2),
            'volume': int(row['Volume'])
        }
        
        return result
        
    except Exception as e:
        print(f"Error fetching data for {full_ticker}: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    # Example 1: TSX stock
    result = get_stock_price('AYA', 'TSX', '9/25/2025')
    if result:
        print(f"\n{result['ticker']} on {result['date']}:")
        print(f"  Open:  ${result['open']}")
        print(f"  Close: ${result['close']}")
    
    # Example 2: NYSE stock
    result2 = get_stock_price('AAPL', 'NYSE', '9/28/2022')
    if result2:
        print(f"\n{result2['ticker']} on {result2['date']}:")
        print(f"  Open:  ${result2['open']}")
        print(f"  Close: ${result2['close']}")

    # Example 3: ETR stock
    result3 = get_stock_price('ETR', 'ADJ', '10/6/2021')
    if result3:
        print(f"\n{result3['ticker']} on {result3['date']}:")
        print(f"  Open:  ${result2['open']}")
        print(f"  Close: ${result2['close']}")