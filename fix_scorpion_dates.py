#!/usr/bin/env python3
"""
Script to fix date formats in scorpion.txt from "Month DD, YYYY" to "MM/DD/YYYY"
"""

from datetime import datetime
import re

def parse_date(date_str):
    """Parse various date formats to MM/DD/YYYY"""
    date_str = date_str.strip()

    # Handle "Month DDth, YYYY" format (e.g., "August 27th, 2018")
    match = re.match(r'^(\w+)\s+(\d+)(?:st|nd|rd|th)?,?\s+(\d{4})$', date_str)
    if match:
        month_name, day, year = match.groups()
        month_num = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }.get(month_name)

        if month_num:
            return f"{month_num}/{day.zfill(2)}/{year}"

    # Handle "Month DD, YYYY" format (e.g., "August 15, 2025")
    match = re.match(r'^(\w+)\s+(\d+),?\s+(\d{4})$', date_str)
    if match:
        month_name, day, year = match.groups()
        month_num = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12'
        }.get(month_name)

        if month_num:
            return f"{month_num}/{day.zfill(2)}/{year}"

    # If no pattern matches, return original (shouldn't happen)
    return date_str

def fix_scorpion_dates():
    """Fix the date formats in scorpion.txt"""

    # Read the file
    with open('scorpion.txt', 'r') as f:
        lines = f.readlines()

    # Process each line
    fixed_lines = []
    for line in lines:
        if line.strip():  # Skip empty lines
            parts = line.strip().split('\t')

            if len(parts) == 3:
                exchange, ticker, date_str = parts
                fixed_date = parse_date(date_str)
                if fixed_date != date_str:
                    print(f"Fixed {ticker}: '{date_str}' -> '{fixed_date}'")
                fixed_lines.append(f"{exchange}\t{ticker}\t{fixed_date}")
            else:
                fixed_lines.append(line.strip())

    # Write the fixed file
    with open('scorpion_fixed.txt', 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')

    print(f"\nFixed file saved as 'scorpion_fixed.txt'")
    print("You can replace the original file by running: copy scorpion_fixed.txt scorpion.txt")

if __name__ == "__main__":
    fix_scorpion_dates()
