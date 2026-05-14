import csv

csv_file = "fullexpenses.csv"

print("Large Spiritwear Expenses:")
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        account = row['Full Account Name']
        if 'Spiritwear' in account and 'Expenses' in account:
            try:
                amt = float(row['Amount Num.'])
            except:
                continue
            if amt > 100:
                print(f"{row['Date']} - {row['Description']} - {row['Number']} - ${amt:.2f}")

