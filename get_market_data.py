# pip install yfinance
import yfinance as yf
from datetime import datetime, timedelta

def get_stock_price(ticker, exchange, date_str):
    """
    Retrieve the opening and closing price for a stock on a specific date.
    All prices and market cap are converted to USD using approximate exchange rates.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AYA')
        exchange (str): Exchange code (e.g., 'TSX', 'NYSE', 'NASDAQ')
        date_str (str): Date in format 'M/D/YYYY' or 'YYYY-MM-DD'
    
    Returns:
        dict: Dictionary containing price data in USD
        Returns None if data is not available
    
    Example:
        >>> result = get_stock_price('AYA', 'TSX', '9/25/2025')
        >>> print(result)
        {'ticker': 'AYA.TO', 'date': '2025-09-25', 'open': 8.42, 'close': 8.63, 'currency': 'USD'}
    """
    # Approximate exchange rates to USD (as of late 2024)
    currency_to_usd = {
        'USD': 1.0,
        'CAD': 0.73,      # Canadian Dollar
        'GBP': 1.27,      # British Pound
        'EUR': 1.08,      # Euro
        'JPY': 0.0067,    # Japanese Yen
        'CNY': 0.14,      # Chinese Yuan
        'HKD': 0.13,      # Hong Kong Dollar
        'AUD': 0.65,      # Australian Dollar
        'NZD': 0.60,      # New Zealand Dollar
        'KRW': 0.00075,   # South Korean Won
        'INR': 0.012,     # Indian Rupee
        'SGD': 0.75,      # Singapore Dollar
        'THB': 0.029,     # Thai Baht
        'IDR': 0.000063,  # Indonesian Rupiah
        'MYR': 0.22,      # Malaysian Ringgit
        'CHF': 1.13,      # Swiss Franc
        'SEK': 0.096,     # Swedish Krona
        'DKK': 0.14,      # Danish Krone
        'NOK': 0.092,     # Norwegian Krone
        'PLN': 0.25,      # Polish Zloty
        'ZAR': 0.055,     # South African Rand
        'ILS': 0.27,      # Israeli Shekel
        'BRL': 0.18,      # Brazilian Real
        'MXN': 0.050,     # Mexican Peso
        'CLP': 0.0010,    # Chilean Peso
        'ARS': 0.0010,    # Argentine Peso
    }
    
    # Exchange to currency mapping
    exchange_currencies = {
        'TSX': 'CAD', 'TSXV': 'CAD',
        'NYSE': 'USD', 'NASDAQ': 'USD', 'AMEX': 'USD', 'OTCMKTS': 'USD', 'OTCQB': 'USD', 'OTCQX': 'USD',
        'LSE': 'GBP',
        'ETR': 'EUR', 'XTRA': 'EUR', 'FRA': 'EUR', 'EPA': 'EUR', 'AMS': 'EUR', 'BRU': 'EUR', 'MIL': 'EUR', 'MCE': 'EUR', 'ELI': 'EUR', 'HEL': 'EUR',
        'SWX': 'CHF',
        'STO': 'SEK',
        'CPH': 'DKK',
        'OSL': 'NOK',
        'WSE': 'PLN',
        'TYO': 'JPY', 'TSE': 'JPY', 'JPX': 'JPY',
        'HKG': 'HKD', 'HK': 'HKD', 'HKEX': 'HKD',
        'SS': 'CNY', 'SHH': 'CNY',
        'SZ': 'CNY', 'SHZ': 'CNY',
        'ASX': 'AUD', 'ASXL': 'AUD',
        'NZE': 'NZD',
        'KRX': 'KRW', 'KOS': 'KRW',
        'BSE': 'INR', 'NSE': 'INR',
        'SGX': 'SGD',
        'SET': 'THB',
        'IDX': 'IDR',
        'MYX': 'MYR',
        'JSE': 'ZAR',
        'TASE': 'ILS',
        'BVMF': 'BRL',
        'BMV': 'MXN',
        'BCS': 'CLP',
        'BCBA': 'ARS',
    }
    
    # Exchange suffix mapping for yfinance
    exchange_suffixes = {
        'TSX': '.TO', 'TSXV': '.V', 'NYSE': '', 'NASDAQ': '', 'AMEX': '', 'OTCMKTS': '', 'OTCQB': '', 'OTCQX': '',
        'LSE': '.L', 'ETR': '.DE', 'XTRA': '.DE', 'FRA': '.F', 'EPA': '.PA', 'AMS': '.AS', 'BRU': '.BR',
        'SWX': '.SW', 'STO': '.ST', 'CPH': '.CO', 'HEL': '.HE', 'OSL': '.OL', 'WSE': '.WA', 'MIL': '.MI',
        'MCE': '.MC', 'ELI': '.LS', 'TYO': '.T', 'TSE': '.T', 'JPX': '.T', 'HKG': '.HK', 'HK': '.HK',
        'HKEX': '.HK', 'SS': '.SS', 'SHH': '.SS', 'SZ': '.SZ', 'SHZ': '.SZ', 'ASX': '.AX', 'ASXL': '.AX',
        'NZE': '.NZ', 'KRX': '.KS', 'KOS': '.KS', 'BSE': '.BO', 'NSE': '.NS', 'SGX': '.SI', 'SET': '.BK',
        'IDX': '.JK', 'MYX': '.KL', 'JSE': '.JO', 'TASE': '.TA', 'BVMF': '.SA', 'BMV': '.MX', 'BCS': '.SN',
        'BCBA': '.BA',
    }
    
    # Get the appropriate suffix and currency
    suffix = exchange_suffixes.get(exchange.upper(), '')
    full_ticker = f"{ticker}{suffix}"
    native_currency = exchange_currencies.get(exchange.upper(), 'USD')
    exchange_rate = currency_to_usd.get(native_currency, 1.0)
    
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
        
        # Calculate historical market cap
        # Market Cap = Share Price × Shares Outstanding
        market_cap = None
        try:
            info = stock.get_info()
            shares_outstanding = info.get('sharesOutstanding', None)
            
            if shares_outstanding:
                # Use closing price for market cap calculation
                closing_price = float(row['Close'])
                market_cap_native = closing_price * shares_outstanding
                market_cap = round(market_cap_native * exchange_rate, 2)
        except Exception as e:
            print(f"Note: Could not calculate market cap - {str(e)}")
        
        result = {
            'ticker': full_ticker,
            'date': target_date_str,
            'open': round(float(row['Open']) * exchange_rate, 2),
            'close': round(float(row['Close']) * exchange_rate, 2),
            'high': round(float(row['High']) * exchange_rate, 2),
            'low': round(float(row['Low']) * exchange_rate, 2),
            'volume': int(row['Volume']),
            'market_cap': market_cap,
            'currency': 'USD',
            'native_currency': native_currency,
            'exchange_rate': round(exchange_rate, 4) if native_currency != 'USD' else None
        }
        
        return result
        
    except Exception as e:
        print(f"Error fetching data for {full_ticker}: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    # Example 1: TSX stock (Canadian exchange, converts CAD to USD)
    result = get_stock_price('SHOP', 'TSX', '9/25/2024')
    if result:
        print(f"\n{result['ticker']} on {result['date']} (in {result['currency']}):")
        print(f"  Open:  ${result['open']}")
        print(f"  Close: ${result['close']}")
        if result['exchange_rate']:
            print(f"  Exchange Rate: 1 {result['native_currency']} = {result['exchange_rate']} USD (approx)")
        if result['market_cap']:
            print(f"  Market Cap: ${result['market_cap']:,.2f}")
    
    # Example 2: NYSE stock (already in USD)
    result2 = get_stock_price('AAPL', 'NYSE', '9/28/2022')
    if result2:
        print(f"\n{result2['ticker']} on {result2['date']} (in {result2['currency']}):")
        print(f"  Open:  ${result2['open']}")
        print(f"  Close: ${result2['close']}")
        if result2['market_cap']:
            print(f"  Market Cap: ${result2['market_cap']:,.2f}")
    
    # Example 3: London Stock Exchange (converts GBP to USD)
    result3 = get_stock_price('BP', 'LSE', '10/6/2021')
    if result3:
        print(f"\n{result3['ticker']} on {result3['date']} (in {result3['currency']}):")
        print(f"  Open:  ${result3['open']}")
        print(f"  Close: ${result3['close']}")
        if result3['exchange_rate']:
            print(f"  Exchange Rate: 1 {result3['native_currency']} = {result3['exchange_rate']} USD (approx)")
        if result3['market_cap']:
            print(f"  Market Cap: ${result3['market_cap']:,.2f}")