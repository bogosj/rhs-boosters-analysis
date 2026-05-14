#!/usr/bin/env python3
"""
Comprehensive price comparison across all receipt markdown files.
Extracts every identifiable item with a price, normalizes names,
and matches items across receipts to find price changes over time.
"""

import glob
import re
import os
import json
from collections import defaultdict
from datetime import datetime

# ── helpers ──────────────────────────────────────────────────────────

def extract_date_from_content(content):
    """Pull the earliest date mentioned in the receipt."""
    patterns = [
        r'(\w+ \d{1,2},?\s*\d{4})',        # "October 2, 2025"
        r'(\d{1,2}/\d{1,2}/\d{4})',          # "10/2/2025"
    ]
    for pat in patterns:
        m = re.search(pat, content)
        if m:
            raw = m.group(1)
            for fmt in ('%B %d, %Y', '%B %d %Y', '%m/%d/%Y'):
                try:
                    return datetime.strptime(raw.replace(',', ''), fmt.replace(',', ''))
                except ValueError:
                    pass
    return None

def academic_year(path):
    if '2024-2025' in path:
        return '2024-2025'
    return '2025-2026'

# Canonical name mapping – hand-tuned for known receipt abbreviations
CANONICAL = {
    # BJ's abbreviations
    'sp watrmelon': 'sour patch watermelon',
    'sourpatchkid': 'sour patch kids',
    'swed sour 24': 'swedish fish/sour patch variety 24ct',
    'swedish fish': 'swedish fish',
    'airheads': 'airheads chewy fruit candy',
    'airheads chewy fruit candy': 'airheads chewy fruit candy',
    'airheads xtremes sweetly sour belts': 'airheads xtremes sour belts',
    'haribo 12ct': 'haribo goldbears 12ct',
    'haribo goldbears': 'haribo goldbears 12ct',
    'haribo goldbear gummi bears': 'haribo goldbears 12ct',
    'one stop': 'one stop candy',
    'one stop candy': 'one stop candy',
    'ss vp 30ct': 'snack stand variety pack 30ct',
    'ccoms16ct': 'cookie combo 16ct',
    'coke 35/12oz': 'coca-cola 35pk cans',
    'coca-cola cans': 'coca-cola 35pk cans',
    'coca-cola cans (35 pk)': 'coca-cola 35pk cans',
    'diet coke soda cans': 'diet coke 35pk cans',
    'diet coke diet soda': 'diet coke 35pk cans',
    'diet coke soda cans (35 pk)': 'diet coke 35pk cans',
    'sprite soda cans': 'sprite 35pk cans',
    'sprite soda cans (35 pk)': 'sprite 35pk cans',
    'brisk tea': 'lipton brisk iced tea',
    'lipton brisk lemon iced tea': 'lipton brisk iced tea',
    'lipton brisk iced tea (36 pk)': 'lipton brisk iced tea',
    'lipton brisk lemon iced tea (36 pk)': 'lipton brisk iced tea',
    'kng sz prtzl': 'king size pretzel',
    'nacho 50ct': 'nacho chips 50ct',
    'cool tangy': 'cool tangy candy',
    'hsy var 30': 'hershey variety 30ct',
    'classic mix': 'classic mix snacks',
    'pick n pack': 'pick n pack candy',
    'welch vr pck': "welch's fruit snacks variety",
    "welch's fruit snacks": "welch's fruit snacks variety",
    'mrcln101': 'mr. clean product',
    'gatorade 20z': 'gatorade 20oz variety',
    'gatorade variety pack': 'gatorade 20oz variety',
    'gatorade liberty variety pack': 'gatorade 20oz variety',
    'tostitos tortilla chips original': 'tostitos tortilla chips',
    'tostitos scoops tortilla chips': 'tostitos scoops chips',
    'heinz tomato ketchup': 'heinz ketchup 3-pack',
    'heinz tomato ketchup (3 pk)': 'heinz ketchup 3-pack',
    'skittles and starburst chewy candy bulk variety pack': 'skittles/starburst variety pack',
    'skittles and starburst chewy candy variety pack': 'skittles/starburst variety pack',
    'skittles and starburst chewy candy variety box': 'skittles/starburst variety pack',
    'skittles and starburst chewy halloween candy bulk variety box (30 ct)': 'skittles/starburst variety pack',
    'sour patch kids & swedish fish variety pack': 'sour patch/swedish fish variety',
    'sour patch kids & swedish fish candy variety pack': 'sour patch/swedish fish variety',
    'frito lay variety pack of snacks and chips (50 ct)': 'frito lay variety 50ct',
    'frito lay variety pack of snacks and chips': 'frito lay variety 50ct',
    'poland spring natural spring water': 'poland spring water',
    'swiss miss milk chocolate hot cocoa': 'swiss miss hot cocoa',
    'ring pops variety box': 'ring pops',
    'nissin cup noodles chicken flavor': 'cup noodles chicken',
    "m&m's full size chocolate candy (48 ct)": "m&m's 48ct",
    'mars full size variety pack': 'mars variety pack',
    'oreo 30 ct': 'oreo 30ct',
    'hambrg rolls': 'hamburger rolls',
    'hotdog rolls': 'hot dog rolls',
    '20 lb propane': '20 lb propane tank',
    'sauc mld ched cq': 'mild cheddar cheese sauce',
    'mild cheddar cheese sauce': 'mild cheddar cheese sauce',
    "chef's quality mild cheddar cheese sauce": 'mild cheddar cheese sauce',
    "chef's quality cheese sauce": 'mild cheddar cheese sauce',
    'pretzel ny jumb 24ct': 'jumbo pretzels 24ct',
    'frozen jumbo pretzels': 'jumbo pretzels (restaurant depot)',
    'frozen jumbo soft pretzels': 'jumbo pretzels (restaurant depot)',
    'frozen jumbo new york pretzels': 'jumbo pretzels (restaurant depot)',
    'frozen beef hamburger patties': 'frozen beef patties',
    'frozen chicken fingers': 'frozen chicken fingers',
    'frozen barber foods crunchie chicken fingers': 'frozen chicken fingers',
    'frozen crunchie chicken fingers': 'frozen chicken fingers',
    'frozen breaded mozzarella sticks': 'frozen mozzarella sticks',
    'frozen battered mozzarella sticks': 'frozen mozzarella sticks',
    'frozen french fries': 'frozen french fries',
    'fun sweets cotton candy': 'cotton candy',
    'classic cotton candy': 'cotton candy',
    'james farm american cheese': 'american cheese slices',
    'sabrett beef franks': 'beef franks',
    'sabrett marathon all beef franks': 'beef franks',
    "nathan's famous skinless beef franks": 'beef franks (nathan\'s)',
    'cupndl chix eng 2.5z': 'cup noodles chicken',
    'cup noodle chicken flavor': 'cup noodles chicken',
    # Apparel
    'paw print t-shirt': 'paw print t-shirt',
    'paw print t-shirt (navy)': 'paw print t-shirt',
    'paw print t-shirts': 'paw print t-shirt',
    'paw print ls shirts': 'paw print long sleeve shirt',
    'paw print ls t-shirt': 'paw print long sleeve shirt',
    'paw print crewneck': 'paw print crewneck',
    'paw print crewnecks': 'paw print crewneck',
    'paw print hoodies': 'paw print hoodie',
    'bulldog crewneck': 'bulldog crewneck',
    'bulldog crewneck (navy)': 'bulldog crewneck',
    'bulldogs navy crewneck': 'bulldog crewneck',
    'bulldog sweatpants': 'bulldog sweatpants',
    'bulldogs sweatpants': 'bulldog sweatpants',
    'bulldog hoodies': 'bulldog hoodie',
    'era crewneck (white)': 'era crewneck',
    'era crewneck (grey)': 'era crewneck',
    'era hoodie (white)': 'era hoodie',
    'era hoodie (grey)': 'era hoodie',
    'fight cancer t-shirt': 'fight cancer t-shirt',
    'fight cancer v-neck': 'fight cancer v-neck',
    'fight cancer ls t-shirt': 'fight cancer long sleeve',
    'fight cancer crewneck': 'fight cancer crewneck',
    'fight cancer hoodie': 'fight cancer hoodie',
    'football t-shirt': 'football t-shirt',
    'r hoodies': 'r hoodie',
    'stripe hoodies': 'stripe hoodie',
    'stripe crewnecks': 'stripe crewneck',
    'bulldog tote bags': 'bulldog tote bag',
    'bulldog duffle bags': 'bulldog duffle bag',
    # Awards
    'captain awards': 'captain award plaque',
    "captains' award plaques": 'captain award plaque',
    'captain awards for spring sports': 'captain award plaque',
    'walnut plaque for captain awards': 'captain award plaque',
    '4 years on varsity awards': '4-year varsity plaque',
    'four years on a varsity sport plaques': '4-year varsity plaque',
    '4 years on a varsity sport awards': '4-year varsity plaque',
    'walnut plaque for 4 years on varsity awards': '4-year varsity plaque',
    'coaches awards': 'coaches award trophy',
    "coaches' award trophies": 'coaches award trophy',
    'coaches awards (trophy)': 'coaches award trophy',
    'large special awards (fecanin, borzotta & balance)': 'special award plaque (large)',
    'bulldog award with extensive engraving': 'bulldog award plaque (special)',
    '12 varsity letter award plaque': '12-letter varsity plaque',
    '3 varsity sports in one year awards': '3-sport varsity plaque',
    # Printing
    'booklets': 'booklets (booster club)',
    # Catering
    'ala carte menu': 'fiesta ala carte menu',
    'adults menu': 'fiesta ala carte menu',
    'soft drinks (unlimited)': 'fiesta unlimited soft drinks',
    'unlimited soft drinks': 'fiesta unlimited soft drinks',
    # Custom blankets
    'custom knit blanket 63" x 63"': 'custom knit blanket 63x63',
}

def normalize(name):
    """Return a canonical name for fuzzy matching."""
    n = name.strip().lower()
    n = re.sub(r'^[-•*]\s*', '', n)
    n = re.sub(r'\s*\(.*?\)\s*$', '', n)  # strip trailing parens
    n = n.strip(' *')
    # Try direct lookup first
    if n in CANONICAL:
        return CANONICAL[n]
    # Try without trailing size info
    n2 = re.sub(r'\s*\d+\s*(oz|ct|pk|lb|pack)\.?$', '', n, flags=re.I)
    if n2 in CANONICAL:
        return CANONICAL[n2]
    return n

# ── extraction ───────────────────────────────────────────────────────

def extract_items_from_md(filepath):
    """Extract (item_name, unit_price, date, receipt_id, vendor) tuples."""
    items = []
    with open(filepath, 'r') as f:
        content = f.read()

    receipt_id = os.path.splitext(os.path.basename(filepath))[0]
    year = academic_year(filepath)
    date = extract_date_from_content(content)
    date_str = date.strftime('%Y-%m-%d') if date else year

    # Identify vendor
    vendor_m = re.search(r'\*\*Vendor:\*\*\s*(.+)', content)
    vendor = vendor_m.group(1).strip() if vendor_m else 'Unknown'

    # ── Strategy 1: Markdown table rows ──
    # Match rows like: | Description | Qty | Price | Amount |
    table_rows = re.findall(
        r'^\|\s*(?!\*\*Total)(?!\*\*Sub)(.+?)\s*\|\s*(\d+)\s*\|\s*\$?([\d,]+\.?\d*)\s*\|\s*\$?([\d,]+\.?\d*)\s*\|',
        content, re.MULTILINE
    )
    for desc, qty, unit_price, total in table_rows:
        desc = desc.strip().strip('*').strip()
        if any(skip in desc.lower() for skip in ['description', '---', 'total', 'subtotal', 'shipping', 'freight',
                                                   'screen charge', 'set up', 'setup', 'trade-in', 'credit',
                                                   'coupon', 'discount', 'tax', 'fee', 'gratuity', 'service charge',
                                                   'room fee']):
            continue
        try:
            up = float(unit_price.replace(',', ''))
            q = int(qty)
            if up > 0 and q > 0:
                items.append({
                    'name': desc,
                    'normalized': normalize(desc),
                    'unit_price': up,
                    'quantity': q,
                    'date': date_str,
                    'receipt': receipt_id,
                    'vendor': vendor,
                    'year': year,
                    'file': filepath,
                })
        except (ValueError, IndexError):
            pass

    # ── Strategy 2: Bullet-point items with prices ──
    # Patterns like: - ITEM ($XX.XX)  or  - ITEM - $XX.XX  or  - ITEM (N units @ $XX.XX)
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line.startswith('-'):
            continue
        if any(skip in line.lower() for skip in ['total', 'tax', 'payment', 'vendor', 'date',
                                                   'amount', 'order', 'gross', 'net', 'fee',
                                                   'discount', 'subtotal', 'shipping', 'receipt',
                                                   'purpose', 'items:', 'savings', 'status',
                                                   'invoice', 'member', 'transaction', 'auth',
                                                   'store', 'cashier', 'terminal', 'coupon',
                                                   'reference', 'approval', 'survey', 'bill to',
                                                   'closing date', 'event', 'contact']):
            continue

        # N units @ $X.XX pattern
        m_unit = re.search(r'(.+?)\s*[-–]\s*(\d+)\s*units?\s*@\s*\$?([\d.]+)', line, re.I)
        if not m_unit:
            m_unit = re.search(r'(.+?)\((\d+)\s*units?\s*@\s*\$?([\d.]+)\)', line, re.I)
        if m_unit:
            desc = re.sub(r'^[-•*]\s*', '', m_unit.group(1)).strip()
            qty = int(m_unit.group(2))
            up = float(m_unit.group(3))
            items.append({
                'name': desc,
                'normalized': normalize(desc),
                'unit_price': up,
                'quantity': qty,
                'date': date_str,
                'receipt': receipt_id,
                'vendor': vendor,
                'year': year,
                'file': filepath,
            })
            continue

        # N @ $X.XX or (N @ $X.XX = $total) pattern
        m_at = re.search(r'(.+?)\s*[-–(]\s*(\d+)\s*@\s*\$?([\d.]+)', line, re.I)
        if m_at:
            desc = re.sub(r'^[-•*]\s*', '', m_at.group(1)).strip()
            qty = int(m_at.group(2))
            up = float(m_at.group(3))
            items.append({
                'name': desc,
                'normalized': normalize(desc),
                'unit_price': up,
                'quantity': qty,
                'date': date_str,
                'receipt': receipt_id,
                'vendor': vendor,
                'year': year,
                'file': filepath,
            })
            continue

        # Simple price: - ITEM ($XX.XX) or - ITEM - $XX.XX
        m_simple = re.search(r'^-\s+(.+?)(?:\s*[-–]\s*|\s+)\(?(\$[\d,.]+)\)?', line)
        if m_simple:
            desc = m_simple.group(1).strip()
            price_str = m_simple.group(2).replace('$', '').replace(',', '')
            # Skip if desc looks like metadata
            if len(desc) < 3 or desc.startswith('**'):
                continue
            try:
                up = float(price_str)
                if 0 < up < 5000:
                    items.append({
                        'name': desc,
                        'normalized': normalize(desc),
                        'unit_price': up,
                        'quantity': 1,
                        'date': date_str,
                        'receipt': receipt_id,
                        'vendor': vendor,
                        'year': year,
                        'file': filepath,
                    })
            except ValueError:
                pass

    return items


# ── main ─────────────────────────────────────────────────────────────

def main():
    md_files = sorted(glob.glob('Receipts/**/*.md', recursive=True))
    all_items = []
    for f in md_files:
        all_items.extend(extract_items_from_md(f))

    # Group by normalized name
    groups = defaultdict(list)
    for item in all_items:
        groups[item['normalized']].append(item)

    # ── Report 1: Items with price differences ──
    print("=" * 80)
    print("COMPREHENSIVE PRICE COMPARISON REPORT")
    print("=" * 80)

    comparisons = []
    for name, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        prices = [e['unit_price'] for e in entries]
        if max(prices) == min(prices):
            continue  # same price everywhere

        min_price = min(prices)
        max_price = max(prices)
        pct = ((max_price - min_price) / min_price) * 100

        comparisons.append({
            'name': name,
            'min_price': min_price,
            'max_price': max_price,
            'pct_change': pct,
            'entries': entries,
        })

    # Sort by percentage change descending
    comparisons.sort(key=lambda x: -x['pct_change'])

    for comp in comparisons:
        print(f"\n{'─' * 60}")
        print(f"  {comp['name'].upper()}")
        print(f"  Min: ${comp['min_price']:.2f}  →  Max: ${comp['max_price']:.2f}  "
              f"(+{comp['pct_change']:.1f}%)")
        print(f"{'─' * 60}")
        # Sort entries by date
        for e in sorted(comp['entries'], key=lambda x: x['date']):
            print(f"    ${e['unit_price']:.2f}  x{e['quantity']}  "
                  f"{e['date']}  {e['receipt']}  ({e['vendor'][:30]})")

    # ── Report 2: Items that appear only once (no comparison possible) ──
    print("\n\n" + "=" * 80)
    print("ITEMS APPEARING ONLY ONCE (no comparison available)")
    print("=" * 80)
    singles = [(name, entries[0]) for name, entries in sorted(groups.items()) if len(entries) == 1]
    for name, e in singles:
        print(f"  ${e['unit_price']:.2f}  {name:<45s}  {e['receipt']}  {e['date']}")

    # ── Report 3: Items with same price across purchases ──
    print("\n\n" + "=" * 80)
    print("ITEMS WITH STABLE PRICING (same price across purchases)")
    print("=" * 80)
    for name, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        prices = [e['unit_price'] for e in entries]
        if max(prices) == min(prices):
            print(f"  ${prices[0]:.2f}  {name:<45s}  ({len(entries)} purchases)")

    # ── Export JSON for dashboard ──
    output = {
        'comparisons': [],
        'stable': [],
        'singles': [],
    }
    for comp in comparisons:
        output['comparisons'].append({
            'name': comp['name'],
            'min_price': comp['min_price'],
            'max_price': comp['max_price'],
            'pct_change': round(comp['pct_change'], 1),
            'entries': [{
                'unit_price': e['unit_price'],
                'quantity': e['quantity'],
                'date': e['date'],
                'receipt': e['receipt'],
                'year': e['year'],
                'vendor': e['vendor'][:50],
            } for e in sorted(comp['entries'], key=lambda x: x['date'])]
        })
    for name, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        prices = [e['unit_price'] for e in entries]
        if max(prices) == min(prices):
            output['stable'].append({
                'name': name,
                'price': prices[0],
                'count': len(entries),
            })
    for name, e in singles:
        output['singles'].append({
            'name': name,
            'price': e['unit_price'],
            'receipt': e['receipt'],
            'date': e['date'],
        })

    with open('analysis/price_comparison.json', 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\n\nJSON exported to analysis/price_comparison.json")
    print(f"Total items extracted: {len(all_items)}")
    print(f"Unique normalized items: {len(groups)}")
    print(f"Items with price changes: {len(comparisons)}")

if __name__ == '__main__':
    main()
