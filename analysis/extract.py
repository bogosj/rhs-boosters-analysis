import glob
import re

md_files = glob.glob("Receipts/**/*.md", recursive=True)

for file in md_files:
    with open(file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            # If line is an item line (starts with - and contains a price)
            if line.startswith('-') and '$' in line and not any(x in line for x in ['Total', 'Tax', 'Payment', 'Vendor', 'Date', 'Amount', 'Order']):
                print(f"{file}: {line}")
