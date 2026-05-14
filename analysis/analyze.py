import os
import csv
import glob
import re
from collections import defaultdict

csv_file = "expenses.csv"
md_files = glob.glob("Receipts/**/*.md", recursive=True)

snack_income = defaultdict(float)
snack_expense = defaultdict(float)

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row['Date']
        if not date: continue
        year = date.split('/')[2]
        month = date.split('/')[0]
        account = row['Full Account Name']
        try:
            amt = float(row['Amount Num.'])
        except:
            amt = 0.0
            
        if 'Snack Shack' in account:
            if 'Income' in account:
                snack_income[year] += amt
            elif 'Expenses' in account:
                snack_expense[year] += amt

print("Snack Shack Income by Year:")
for y in sorted(snack_income.keys()):
    print(f"  {y}: ${snack_income[y]:.2f}")

print("\nSnack Shack Expenses by Year:")
for y in sorted(snack_expense.keys()):
    print(f"  {y}: ${snack_expense[y]:.2f}")

print("\nExtracting Item Prices from Markdown...")
items = []
for file in md_files:
    with open(file, 'r') as f:
        content = f.read()
        # Look for patterns like:
        # - **Receipt Apr 20:** $63.00 - 4 units of 20 LB Propane
        # - PAW PRINT T-SHIRT (NAVY) - 1 unit @ $16.00
        # - 40 units of Gatorade @ $1.50
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line.startswith('-'): continue
            
            # Pattern 1: $X - Y units of Z
            m1 = re.search(r'\$([\d\.]+)\s*-\s*(\d+)\s*units? of\s*(.*)', line, re.IGNORECASE)
            if m1:
                price = float(m1.group(1))
                qty = float(m1.group(2))
                name = m1.group(3).strip()
                # remove parentheticals like payment methods
                name = re.sub(r'\(.*?\)', '', name).strip()
                unit_price = price / qty
                items.append((file, name, unit_price, qty, price))
                continue
                
            # Pattern 2: Z - Y units @ $X
            m2 = re.search(r'(.*?)\s*-\s*(\d+)\s*units? @ \$([\d\.]+)', line, re.IGNORECASE)
            if m2:
                name = m2.group(1).strip()
                name = re.sub(r'^\-\s*', '', name) # remove leading dash
                qty = float(m2.group(2))
                unit_price = float(m2.group(3))
                items.append((file, name, unit_price, qty, qty * unit_price))
                continue
                
            # Pattern 3: Z - $X
            if "Total" not in line and "Order" not in line and "Receipt" not in line and "Date" not in line and "Vendor" not in line:
                 m3 = re.search(r'^\-\s*(.*?)\s*[\-:]\s*\$([\d\.]+)', line)
                 if m3:
                     name = m3.group(1).strip()
                     name = re.sub(r'\*\*(.*?)\*\*', r'\1', name)
                     price = float(m3.group(2))
                     # items.append((file, name, price, 1, price))

# Group items by normalized name
grouped = defaultdict(list)
for file, name, unit_price, qty, total in items:
    # simple normalization
    norm = name.lower()
    if 'propane' in norm: norm = 'propane 20lb'
    elif 'gatorade' in norm: norm = 'gatorade'
    elif 'water' in norm: norm = 'water'
    elif 'burger' in norm or 'beef patt' in norm: norm = 'beef patties'
    elif 'franks' in norm or 'hot dog' in norm: norm = 'hot dogs'
    elif 'buns' in norm or 'rolls' in norm: norm = 'rolls'
    elif 'candy' in norm: norm = 'candy'
    elif 'sweet relish' in norm: norm = 'relish'
    elif 'cheese' in norm and 'sauce' not in norm: norm = 'american cheese'
    elif 'crinkle fries' in norm or 'french fries' in norm: norm = 'french fries'
    
    # Extract year from file path
    year = '2024'
    if '2025-2026' in file: year = '2025'
    elif '2024-2025' in file: year = '2024'
        
    grouped[norm].append((year, unit_price, file))

for k in sorted(grouped.keys()):
    if len(grouped[k]) > 1:
        print(f"\nItem: {k}")
        for year, price, file in grouped[k]:
             print(f"  {year}: ${price:.2f} ({file})")

