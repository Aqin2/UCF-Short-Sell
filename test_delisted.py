import yfinance as yf
from datetime import datetime, timedelta

# Test ticker
symbol = "EVA"

print(f"Testing {symbol}...")
print("=" * 60)

# Test 1: Get all available history
print("\n1. Fetching max history with Ticker.history():")
try:
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="max")
    
    if not hist.empty:
        print(f"   SUCCESS! Data from {hist.index[0].date()} to {hist.index[-1].date()}")
        print(f"   Total records: {len(hist)}")
        print(f"\n   Last 5 records:")
        print(hist.tail())
    else:
        print("   FAILED: No data returned")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Try with yf.download()
print("\n2. Fetching with yf.download():")
try:
    hist2 = yf.download(symbol, period="max", progress=False)
    
    if not hist2.empty:
        print(f"   SUCCESS! Data from {hist2.index[0].date()} to {hist2.index[-1].date()}")
        print(f"   Total records: {len(hist2)}")
    else:
        print("   FAILED: No data returned")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Try a specific date range (adjust these dates as needed)
print("\n3. Fetching specific date range (2020-2023):")
try:
    hist3 = yf.download(symbol, start="2020-01-01", end="2023-12-31", progress=False)
    
    if not hist3.empty:
        print(f"   SUCCESS! Data from {hist3.index[0].date()} to {hist3.index[-1].date()}")
        print(f"   Total records: {len(hist3)}")
    else:
        print("   FAILED: No data returned")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Get info about the ticker
print("\n4. Getting ticker info:")
try:
    info = ticker.info
    if info:
        print(f"   Company: {info.get('longName', 'N/A')}")
        print(f"   Exchange: {info.get('exchange', 'N/A')}")
        print(f"   Quote Type: {info.get('quoteType', 'N/A')}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)