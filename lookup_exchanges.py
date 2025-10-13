#!/usr/bin/env python3
"""
Script to look up exchange information for stock tickers using yfinance
"""

import yfinance as yf
import time
from datetime import datetime

def get_exchange_info(ticker):
    """Get exchange information for a ticker using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Try to get exchange info from various fields
        exchange = None

        # Check different possible fields for exchange info
        if 'exchange' in info and info['exchange']:
            exchange = info['exchange']

        # Map common exchange codes to more readable names
        exchange_map = {
            'NMS': 'NASDAQ',
            'NYQ': 'NYSE',
            'NGM': 'NASDAQ',
            'ASE': 'AMEX',
            'PCX': 'AMEX',
            'OTC': 'OTCMKTS',
            'PNK': 'OTCMKTS',
            'BATS': 'BATS',
            'TOR': 'TSX',
            'VAN': 'TSXV',
            'CNQ': 'TSXV',
            'LSE': 'LSE',
            'FRA': 'XETR',
            'ETR': 'XETR',
            'BER': 'XETR',
            'MUN': 'XETR',
            'DUS': 'XETR',
            'HAM': 'XETR',
            'STU': 'XETR',
            'HKG': 'HKEX',
            'SHH': 'SSE',
            'SHE': 'SZSE',
            'TYO': 'JPX',
            'TSE': 'JPX',
            'ASX': 'ASX',
            'KRX': 'KRX',
            'TAI': 'TWSE',
            'SGX': 'SGX',
            'BSE': 'BSE',
            'NSE': 'NSE',
            'JSE': 'JSE',
            'SAU': 'TADAWUL'
        }

        if exchange and exchange in exchange_map:
            exchange = exchange_map[exchange]

        # If we still don't have exchange, try to infer from ticker patterns
        if not exchange:
            if ticker.endswith('.TO'):
                exchange = 'TSX'
            elif ticker.endswith('.V'):
                exchange = 'TSXV'
            elif ticker.endswith('.L'):
                exchange = 'LSE'
            elif ticker.endswith('.DE'):
                exchange = 'XETR'
            elif ticker.endswith('.HK'):
                exchange = 'HKEX'
            elif ticker.endswith('.SS'):
                exchange = 'SSE'
            elif ticker.endswith('.SZ'):
                exchange = 'SZSE'
            elif ticker.endswith('.T'):
                exchange = 'JPX'
            elif ticker.endswith('.AX'):
                exchange = 'ASX'
            elif ticker.endswith('.KR'):
                exchange = 'KRX'
            elif ticker.endswith('.TW'):
                exchange = 'TWSE'
            elif ticker.endswith('.SI'):
                exchange = 'SGX'
            elif ticker.endswith('.NS'):
                exchange = 'NSE'
            elif ticker.endswith('.BO'):
                exchange = 'BSE'
            elif ticker.endswith('.JO'):
                exchange = 'JSE'
            elif ticker.endswith('.SR'):
                exchange = 'TADAWUL'

        return exchange, info

    except Exception as e:
        print(f"Error looking up {ticker}: {str(e)}")
        return None, None

def main():
    # Tickers that need exchange information
    tickers_to_lookup = [
        'ELF', 'KDNY', 'DLO', 'RUN', 'HASI', 'BEKE', 'DNMR',
        'XL', 'YY', 'NNOX', 'GSX', 'EHTH', 'INGN', 'MFC', 'TAL', 'CIFS'
    ]

    print("Looking up exchange information for tickers...")
    print("=" * 50)

    results = {}

    for ticker in tickers_to_lookup:
        print(f"Looking up {ticker}...")
        exchange, info = get_exchange_info(ticker)

        if exchange:
            results[ticker] = exchange
            print(f"  ✓ {ticker}: {exchange}")
        else:
            print(f"  ✗ {ticker}: Could not determine exchange")

        # Be nice to the API
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("=" * 50)

    for ticker, exchange in results.items():
        print(f"{ticker}: {exchange}")

    return results

if __name__ == "__main__":
    main()
