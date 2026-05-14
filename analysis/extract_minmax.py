import glob
import re
from collections import defaultdict

md_files = glob.glob("Receipts/**/*.md", recursive=True)

items = defaultdict(list)

for file in md_files:
    with open(file, 'r') as f:
        content = f.read()
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Simple heuristic for items
            if line.startswith('-') and '$' in line and not any(x in line.lower() for x in ['total', 'tax', 'payment', 'vendor', 'date', 'amount', 'order', 'gross', 'net', 'fee', 'discount', 'subtotal', 'shipping', 'receipt', 'purpose', 'items:', 'savings']):
                # Find unit price if pattern: Z - Y units @ $X
                m2 = re.search(r'(.*?)\s*-\s*(\d+)\s*units? @ \$([\d\.]+)', line, re.IGNORECASE)
                if m2:
                    name = m2.group(1).strip()
                    name = re.sub(r'^\-\s*', '', name)
                    unit_price = float(m2.group(3))
                    items[name.lower()].append((unit_price, file, line))
                    continue
                
                # Z (Y units @ $X)
                m3 = re.search(r'(.*?)\(\s*(\d+)\s*units? @ \$([\d\.]+)\)', line, re.IGNORECASE)
                if m3:
                    name = m3.group(1).strip()
                    name = re.sub(r'^\-\s*', '', name)
                    unit_price = float(m3.group(3))
                    items[name.lower()].append((unit_price, file, line))
                    continue

print("Price differences found:")
for name, data in items.items():
    if len(data) > 1:
        prices = [d[0] for d in data]
        if max(prices) != min(prices):
            print(f"\nItem: {name}")
            for price, file, line in data:
                print(f"  ${price:.2f} in {file}: {line}")
