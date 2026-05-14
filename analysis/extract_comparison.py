import glob
import re
from collections import defaultdict

md_files = glob.glob("Receipts/**/*.md", recursive=True)

items_by_year = defaultdict(list)

for file in md_files:
    year = '2024-2025' if '2024-2025' in file else '2025-2026'
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('-') and '$' in line and not any(x in line for x in ['Total', 'Tax', 'Payment', 'Vendor', 'Date', 'Amount', 'Order', 'Gross', 'Net', 'Fee']):
                items_by_year[year].append(line)

print("2024-2025 ITEMS:")
for i in items_by_year['2024-2025']:
    if any(word in i.lower() for word in ['candy', 'soda', 'coke', 'chip', 'burger', 'dog', 'beef', 'water', 'gatorade', 'pretzel']):
        print(i)

print("\n2025-2026 ITEMS:")
for i in items_by_year['2025-2026']:
    if any(word in i.lower() for word in ['candy', 'soda', 'coke', 'chip', 'burger', 'dog', 'beef', 'water', 'gatorade', 'pretzel']):
        print(i)

