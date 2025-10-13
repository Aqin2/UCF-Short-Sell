#!/usr/bin/env python3
"""
Script to merge all .out files into one combined file with a Firm column
"""

import glob
import os

def get_firm_name(filename):
    """Extract firm name from filename (remove .txt.out and format)"""
    # Remove .txt.out extension
    name = filename.replace('.txt.out', '')

    # Replace underscores with spaces and capitalize words
    name = name.replace('_', ' ').title()

    return name

def merge_out_files():
    """Merge all .out files into one combined file"""

    # Get all .out files
    out_files = glob.glob('*.txt.out')

    if not out_files:
        print("No .out files found!")
        return

    print(f"Found {len(out_files)} .out files to merge:")
    for file in out_files:
        print(f"  - {file}")

    # Combined data will be stored here
    combined_data = []

    # Process each file
    for i, filename in enumerate(sorted(out_files)):
        firm_name = get_firm_name(filename)
        print(f"\nProcessing {filename} (Firm: {firm_name})...")

        with open(filename, 'r') as f:
            lines = f.readlines()

        data_count = 0
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            if line_num == 0:  # Header row
                if i == 0:  # Only add header once
                    # Add Firm column to header
                    combined_data.append(f"Firm,{line}")
                continue

            # Data row - add firm name as first column
            combined_data.append(f"{firm_name},{line}")
            data_count += 1

        print(f"  Added {data_count} data rows")

    # Write combined file
    output_filename = "all_firms_combined.csv"
    with open(output_filename, 'w') as f:
        for line in combined_data:
            f.write(line + '\n')

    print(f"\n✅ Successfully merged all files into '{output_filename}'")
    print(f"Total rows: {len(combined_data)}")
    print(f"  - Header: 1 row")
    print(f"  - Data: {len(combined_data) - 1} rows")

    # Show sample of the output
    print(f"\n📋 Sample of merged data:")
    for i, line in enumerate(combined_data[:5]):
        print(f"  {line}")
    if len(combined_data) > 5:
        print(f"  ... ({len(combined_data) - 5} more rows)")

if __name__ == "__main__":
    merge_out_files()
