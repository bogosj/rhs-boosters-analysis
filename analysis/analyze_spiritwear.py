import csv
import glob
import re
from collections import defaultdict

csv_file = "fullexpenses.csv"

income = defaultdict(float)
expense = defaultdict(float)

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row['Date']
        if not date: continue
        
        # skip year-end closing transactions
        if "Income from" in row['Description']: continue
        
        try:
            month, day, year = map(int, date.split('/'))
        except:
            continue
        
        if month >= 8:
            acad_year = f"{year}-{year+1}"
        else:
            acad_year = f"{year-1}-{year}"
            
        account = row['Full Account Name']
        try:
            amt = float(row['Amount Num.'])
        except:
            amt = 0.0
            
        if 'Spiritwear' in account:
            if 'Income' in account:
                income[acad_year] += -amt
            elif 'Expenses' in account:
                expense[acad_year] += amt

print("Spiritwear Financials by Academic Year (fullexpenses.csv):")
for y in sorted(set(income.keys()) | set(expense.keys())):
    inc = income[y]
    exp = expense[y]
    prof = inc - exp
    print(f"{y}: Income: ${inc:.2f}, Expenses: ${exp:.2f}, Profit: ${prof:.2f}")

md_files = glob.glob("Receipts/**/*.md", recursive=True)
items_by_year = defaultdict(list)

for file in md_files:
    year = '2024-2025' if '2024-2025' in file else '2025-2026'
    with open(file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('-') and '$' in line and not any(x in line.lower() for x in ['total', 'tax', 'payment', 'vendor', 'date', 'amount', 'order', 'gross', 'net', 'fee']):
                items_by_year[year].append((file, line))

spiritwear_keywords = ['shirt', 'hoodie', 'crewneck', 'blanket', 'sweatshirt', 'apparel', 'hat', 'cap', 'beanie', 'fleece']

for y in ['2024-2025', '2025-2026']:
    print(f"\n{y} SPIRITWEAR ITEMS:")
    for f, i in items_by_year[y]:
        if any(word in i.lower() for word in spiritwear_keywords):
            print(f"{f}: {i}")

