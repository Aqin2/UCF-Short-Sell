# pip install polygon-api-client
from polygon import RESTClient
from datetime import datetime, timedelta

def get_stock_price(ticker, exchange, date_str, api_key=""):
    """
    Retrieve the open/close price for a stock on a specific date from Polygon.io.
    All prices and market cap are converted to USD using approximate exchange rates.
    
    Supports delisted stocks, historical data, and major exchanges.
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
        'NYSE': 'USD', 'NASDAQ': 'USD', 'AMEX': 'USD', 'OTCMKTS': 'USD',
        'LSE': 'GBP',
        'ETR': 'EUR', 'FRA': 'EUR', 'EPA': 'EUR', 'AMS': 'EUR',
        'BVMF': 'BRL', 'BMV': 'MXN',
        'TYO': 'JPY', 'TSE': 'JPY',
        'HKG': 'HKD', 'HK': 'HKD',
        'ASX': 'AUD',
        'SGX': 'SGD',
        'BSE': 'INR', 'NSE': 'INR',
        'SWX': 'CHF',
        'STO': 'SEK',
        'CPH': 'DKK',
        'OSL': 'NOK',
    }
    
    # Exchange suffix mapping for compatibility with Yahoo-style tickers
    exchange_suffixes = {
        'TSX': '.TO', 'TSXV': '.V', 'NYSE': '', 'NASDAQ': '',
        'AMEX': '', 'OTCMKTS': '', 'LSE': '.L', 'ETR': '.DE', 'FRA': '.F',
        'EPA': '.PA', 'AMS': '.AS', 'BVMF': '.SA', 'BMV': '.MX'
    }
    
    suffix = exchange_suffixes.get(exchange.upper(), '')
    full_ticker = f"{ticker}{suffix}"
    
    # Get the currency for this exchange
    native_currency = exchange_currencies.get(exchange.upper(), 'USD')
    exchange_rate = currency_to_usd.get(native_currency, 1.0)
    
    # Parse date
    try:
        if '/' in date_str:
            target_date = datetime.strptime(date_str, '%m/%d/%Y')
        else:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Use 'M/D/YYYY' or 'YYYY-MM-DD'")
        return None
    
    # Polygon expects YYYY-MM-DD
    date_str = target_date.strftime('%Y-%m-%d')
    
    # Polygon uses raw tickers like 'EVA' or 'AAPL' — no suffixes
    # Canadian and European tickers may not be supported on Polygon
    symbol = ticker if exchange.upper() in ['NYSE', 'NASDAQ', 'AMEX', 'OTCMKTS'] else full_ticker
    
    try:
        client = RESTClient(api_key)
        
        # Fetch open/close data for that day
        resp = client.get_daily_open_close_agg(symbol, date_str)
        
        if not resp:
            print(f"No data found for {symbol} on {date_str}")
            return None
        
        # Calculate historical market cap
        # Market Cap = Share Price × Shares Outstanding
        market_cap = None
        try:
            ticker_details = client.get_ticker_details(symbol)
            
            # Get current shares outstanding
            shares_outstanding = getattr(ticker_details, 'weighted_shares_outstanding', None) or \
                               getattr(ticker_details, 'share_class_shares_outstanding', None)
            
            if shares_outstanding:
                # Use historical closing price for market cap calculation
                closing_price = float(resp.close)
                market_cap_native = closing_price * shares_outstanding
                market_cap = round(market_cap_native * exchange_rate, 2)
        except Exception as e:
            print(f"Note: Could not calculate market cap - {str(e)}")

        result = {
            'ticker': symbol,
            'date': date_str,
            'open': round(float(resp.open) * exchange_rate, 2),
            'close': round(float(resp.close) * exchange_rate, 2),
            'high': round(float(resp.high) * exchange_rate, 2),
            'low': round(float(resp.low) * exchange_rate, 2),
            'volume': int(resp.volume),
            'market_cap': market_cap,
            'currency': 'USD',
            'native_currency': native_currency,
            'exchange_rate': round(exchange_rate, 4) if native_currency != 'USD' else None
        }
        return result
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # UCF Polygon API key
    POLYGON_API_KEY = ""

    # Example 1: Delisted stock (Enviva, NYSE:EVA)
    result = get_stock_price('EVA', 'NYSE', '2023-10-02', POLYGON_API_KEY)
    if result:
        print(f"\n{result['ticker']} on {result['date']} (in {result['currency']}):")
        print(f"  Open:  ${result['open']}")
        print(f"  Close: ${result['close']}")
        print(f"  Volume: {result['volume']:,}")
        if result['market_cap']:
            print(f"  Market Cap: ${result['market_cap']:,.2f}")

    # Example 2: Active stock
    result2 = get_stock_price('AAPL', 'NASDAQ', '2022-09-28', POLYGON_API_KEY)
    if result2:
        print(f"\n{result2['ticker']} on {result2['date']} (in {result2['currency']}):")
        print(f"  Open:  ${result2['open']}")
        print(f"  Close: ${result2['close']}")
        if result2['market_cap']:
            print(f"  Market Cap: ${result2['market_cap']:,.2f}")
