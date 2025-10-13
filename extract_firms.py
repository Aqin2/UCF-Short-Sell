import csv
import os

def extract_firms_from_csv(csv_file_path):
    """Extract firm data from CSV and create separate text files for each firm."""

    # Define the firms and their column positions
    firms = {
        'Viceroy': (1, 2, 3),      # columns 2,3,4 (0-indexed: 1,2,3)
        'Hindenberg': (5, 6, 7),   # columns 6,7,8 (0-indexed: 5,6,7)
        'Spruce Point': (9, 10, 11), # columns 10,11,12 (0-indexed: 9,10,11)
        'Muddy Waters': (13, 14, 15), # columns 14,15,16 (0-indexed: 13,14,15)
        'Scorpion': (17, 18, 19),   # columns 18,19,20 (0-indexed: 17,18,19)
        'Blue Orca': (21, 22, 23),  # columns 22,23,24 (0-indexed: 21,22,23)
        'Fuzzy Panda': (25, 26, 27) # columns 26,27,28 (0-indexed: 25,26,27)
    }

    # Read the CSV file
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # Skip the first row (firm names)
        next(reader)

        # Read the header row
        headers = next(reader)

        # Initialize data storage for each firm
        firm_data = {firm: [] for firm in firms.keys()}

        # Process each row
        for row in reader:
            for firm, (exchange_col, ticker_col, date_col) in firms.items():
                # Check if the row has data for this firm's columns
                if len(row) > date_col:  # Make sure the row has enough columns
                    exchange = row[exchange_col].strip() if row[exchange_col].strip() else ''
                    ticker = row[ticker_col].strip() if row[ticker_col].strip() else ''
                    date = row[date_col].strip() if row[date_col].strip() else ''

                    # Only add if we have at least some data
                    if exchange or ticker or date:
                        firm_data[firm].append([exchange, ticker, date])

    # Write each firm's data to a separate file
    for firm, data in firm_data.items():
        if data:  # Only create file if there's data
            filename = firm.lower().replace(' ', '_') + '.txt'
            filepath = os.path.join(os.path.dirname(csv_file_path), filename)

            with open(filepath, 'w', newline='', encoding='utf-8') as txtfile:
                # Write header
                txtfile.write("Stock Exchange\tStock Ticker\tDate Published\n")

                # Write data rows
                for row in data:
                    txtfile.write('\t'.join(row) + '\n')

            print(f"Created {filename} with {len(data)} entries")

if __name__ == "__main__":
    csv_file = "Short Activist Data - Sheet1.csv"
    extract_firms_from_csv(csv_file)
