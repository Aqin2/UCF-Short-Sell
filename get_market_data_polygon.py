# pip install polygon-api-client
from polygon import RESTClient
from datetime import datetime, timedelta

def get_stock_price(ticker, exchange, date_str, api_key="tn4NSpJrJycbY85Tn2rUcuEo_JER8jqR"):
    """
    Retrieve the open/close price for a stock on a specific date from Polygon.io.
    
    Supports delisted stocks, historical data, and major exchanges.
    """
    
    # Exchange suffix mapping for compatibility with Yahoo-style tickers
    exchange_suffixes = {
        'TSX': '.TO', 'TSXV': '.V', 'NYSE': '', 'NASDAQ': '',
        'AMEX': '', 'OTCMKTS': '', 'LSE': '.L', 'ETR': '.DE', 'FRA': '.F',
        'EPA': '.PA', 'AMS': '.AS', 'BVMF': '.SA', 'BMV': '.MX'
    }
    
    suffix = exchange_suffixes.get(exchange.upper(), '')
    full_ticker = f"{ticker}{suffix}"
    
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
        
        result = {
            'ticker': symbol,
            'date': date_str,
            'open': round(float(resp.open), 2),
            'close': round(float(resp.close), 2),
            'high': round(float(resp.high), 2),
            'low': round(float(resp.low), 2),
            'volume': int(resp.volume)
        }
        return result
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # UCF Polygon API key
    POLYGON_API_KEY = "tn4NSpJrJycbY85Tn2rUcuEo_JER8jqR"

    # Example 1: Delisted stock (Enviva, NYSE:EVA)
    result = get_stock_price('EVA', 'NYSE', '2023-10-02', POLYGON_API_KEY)
    if result:
        print(f"\n{result['ticker']} on {result['date']}:")
        print(f"  Open:  ${result['open']}")
        print(f"  Close: ${result['close']}")
        print(f"  Volume: {result['volume']:,}")

    # Example 2: Active stock
    result2 = get_stock_price('AAPL', 'NASDAQ', '2022-09-28', POLYGON_API_KEY)
    if result2:
        print(f"\n{result2['ticker']} on {result2['date']}:")
        print(f"  Open:  ${result2['open']}")
        print(f"  Close: ${result2['close']}")
