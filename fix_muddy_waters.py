#!/usr/bin/env python3
"""
Script to fix muddy_waters.txt by filling in missing exchange information
"""

def fix_muddy_waters():
    """Fix the muddy_waters.txt file by adding missing exchange information"""

    # Exchange mappings we found
    exchange_map = {
        'ELF': 'NYSE',
        'KDNY': 'NASDAQ',  # Assuming NASDAQ for this small cap
        'DLO': 'NASDAQ',
        'RUN': 'NASDAQ',
        'HASI': 'NYSE',
        'BEKE': 'NYSE',
        'DNMR': 'OTCMKTS',
        'XL': 'NYSE',      # XL Fleet Corp was NYSE
        'YY': 'NASDAQ',    # YY Inc. trades on NASDAQ
        'NNOX': 'NASDAQ',
        'GSX': 'BATS',     # Using BATS instead of BTS
        'EHTH': 'NASDAQ',
        'INGN': 'NASDAQ',
        'MFC': 'NYSE',
        'TAL': 'NYSE',
        'CIFS': 'OTCMKTS'  # China Internet Nationwide was OTC
    }

    # Read the file
    with open('muddy_waters.txt', 'r') as f:
        lines = f.readlines()

    # Process each line
    fixed_lines = []
    for line in lines:
        if line.strip():  # Skip empty lines
            parts = line.strip().split('\t')

            if len(parts) == 3:
                # Normal line with exchange, ticker, date
                exchange, ticker, date = parts[0], parts[1], parts[2]

                # If exchange is empty or just whitespace, fill it in
                if not exchange.strip() and ticker in exchange_map:
                    exchange = exchange_map[ticker]
                    print(f"Fixed {ticker}: added exchange {exchange}")

                fixed_lines.append(f"{exchange}\t{ticker}\t{date}")

            elif len(parts) == 2:
                # Line missing exchange - parts are [ticker, date]
                ticker, date = parts[0], parts[1]

                if ticker in exchange_map:
                    exchange = exchange_map[ticker]
                    print(f"Fixed {ticker}: added exchange {exchange}")
                    fixed_lines.append(f"{exchange}\t{ticker}\t{date}")
                else:
                    # Keep as is if we don't know the exchange
                    fixed_lines.append(line.strip())
            else:
                # Header or other format
                fixed_lines.append(line.strip())

    # Write the fixed file
    with open('muddy_waters_fixed.txt', 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')

    print(f"\nFixed file saved as 'muddy_waters_fixed.txt'")
    print("You can replace the original file by running: mv muddy_waters_fixed.txt muddy_waters.txt")

if __name__ == "__main__":
    fix_muddy_waters()
