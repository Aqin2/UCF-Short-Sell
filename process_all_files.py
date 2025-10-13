#!/usr/bin/env python3
"""
Script to process all .txt files with get_data.py
"""

import os
import subprocess
import glob

def main():
    # Get all .txt files in current directory
    txt_files = glob.glob('*.txt')

    # Filter out files that already have .out files (already processed)
    txt_files = [f for f in txt_files if not os.path.exists(f + '.out')]

    print(f"Found {len(txt_files)} .txt files to process: {txt_files}")

    for txt_file in txt_files:
        print(f"\nProcessing {txt_file}...")
        try:
            # Run get_data.py with the current file
            result = subprocess.run(['python', 'get_data.py', txt_file],
                                  capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print(f"✓ Successfully processed {txt_file}")
                if result.stdout:
                    print(f"Output: {result.stdout[:200]}...")  # Show first 200 chars
            else:
                print(f"✗ Error processing {txt_file}: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"✗ Timeout processing {txt_file} (took longer than 5 minutes)")
        except Exception as e:
            print(f"✗ Exception processing {txt_file}: {str(e)}")

    print("\nProcessing complete!")

if __name__ == "__main__":
    main()
