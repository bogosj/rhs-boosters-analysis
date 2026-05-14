import csv
from collections import defaultdict

csv_file = "expenses.csv"

income = defaultdict(float)
expense = defaultdict(float)

with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date = row['Date']
        if not date: continue
        
        # skip year-end closing transactions
        if "Income from" in row['Description']: continue
        
        month, day, year = map(int, date.split('/'))
        
        # Determine academic year
        if month >= 8:
            acad_year = f"{year}-{year+1}"
        else:
            acad_year = f"{year-1}-{year}"
            
        account = row['Full Account Name']
        try:
            amt = float(row['Amount Num.'])
        except:
            amt = 0.0
            
        if 'Snack Shack' in account:
            if 'Income' in account:
                income[acad_year] += -amt
            elif 'Expenses' in account:
                expense[acad_year] += amt

print("Snack Shack Financials by Academic Year (Excluding Closing Entries):")
for y in sorted(set(income.keys()) | set(expense.keys())):
    inc = income[y]
    exp = expense[y]
    prof = inc - exp
    print(f"{y}: Income: ${inc:.2f}, Expenses: ${exp:.2f}, Profit: ${prof:.2f}")

