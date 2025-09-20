#!/usr/bin/env python3
"""
Budget Tracker CLI
- Stores expenses in a local CSV file
- Commands: add, list, summary, monthly, categories, delete
- CSV schema: date, description, category, amount
"""
import csv
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "expenses.csv"

CATEGORIES = [
    "food", "transport", "rent", "utilities", "entertainment",
    "health", "education", "clothes", "misc"
]

def ensure_csv():
    if not DATA_FILE.exists():
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date","description","category","amount"])

def parse_amount(s: str) -> float:
    try:
        return round(float(s), 2)
    except Exception:
        print(" Amount must be a number. Example: 12.50")
        sys.exit(1)

def valid_date(s: str) -> str:
    # Accept YYYY-MM-DD; default to today if 'today' or empty is given in interactive prompts
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return s
    except ValueError:
        print(" Date must be in YYYY-MM-DD format, e.g., 2025-09-20.")
        sys.exit(1)

def add_expense(date: str, description: str, category: str, amount: float):
    ensure_csv()
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, description, category.lower(), f"{amount:.2f}"])
    print(f" Added: {date} | {description} | {category} | ${amount:.2f}")

def list_expenses(limit=None):
    ensure_csv()
    rows = read_rows()
    if limit:
        rows = rows[-limit:]
    total = 0.0
    print("—" * 72)
    print(f"{'DATE':10}  {'DESCRIPTION':28}  {'CATEGORY':14}  {'AMOUNT':>10}")
    print("—" * 72)
    for r in rows:
        amt = float(r['amount'])
        total += amt
        print(f"{r['date']:10}  {r['description'][:28]:28}  {r['category'][:14]:14}  ${amt:>9.2f}")
    print("—" * 72)
    print(f"{'TOTAL':56}  ${total:>9.2f}")

def category_summary():
    ensure_csv()
    rows = read_rows()
    sums = {}
    for r in rows:
        cat = r["category"]
        sums[cat] = sums.get(cat, 0.0) + float(r["amount"])
    print("—" * 40)
    print(f"{'CATEGORY':14}  {'TOTAL':>10}")
    print("—" * 40)
    for cat, total in sorted(sums.items(), key=lambda x: -x[1]):
        print(f"{cat:14}  ${total:>9.2f}")
    print("—" * 40)

def monthly_summary(year_month: str):
    """
    year_month: 'YYYY-MM' (e.g., 2025-09)
    """
    ensure_csv()
    try:
        datetime.strptime(year_month + "-01", "%Y-%m-%d")
    except ValueError:
        print(" Month must be in 'YYYY-MM' format, e.g., 2025-09.")
        sys.exit(1)

    rows = read_rows()
    monthly_rows = [r for r in rows if r["date"].startswith(year_month)]
    total = sum(float(r["amount"]) for r in monthly_rows)
    print(f"📆 Monthly Summary for {year_month}")
    print("—" * 40)
    for r in monthly_rows:
        print(f"{r['date']}  {r['description']}  {r['category']}  ${float(r['amount']):.2f}")
    print("—" * 40)
    print(f"TOTAL: ${total:.2f}")

def list_categories():
    print("Available categories:")
    for c in CATEGORIES:
        print(f" - {c}")

def delete_expense(index: int):
    ensure_csv()
    rows = read_rows()
    if index < 1 or index > len(rows):
        print(f" Invalid index. Use 1..{len(rows)}")
        sys.exit(1)
    removed = rows.pop(index - 1)
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date","description","category","amount"])
        for r in rows:
            writer.writerow([r["date"], r["description"], r["category"], r["amount"]])
    print(f" Deleted #{index}: {removed['date']} | {removed['description']} | {removed['category']} | ${removed['amount']}")

def read_rows():
    ensure_csv()
    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)

def interactive():
    ensure_csv()
    print("💸 Budget Tracker CLI — Interactive Mode")
    print("Type 'help' for commands. 'quit' to exit.\n")
    while True:
        cmd = input("> ").strip().lower()
        if cmd in ("quit", "exit"):
            break
        if cmd in ("help", "?"):
            print("""
Commands:
  add            Add an expense
  list [N]       List all expenses (or last N)
  summary        Show total by category
  monthly YYYY-MM  Show expenses for a month
  categories     Show available categories
  delete N       Delete the N-th expense (from list order)
  quit           Exit
""")
            continue
        if cmd.startswith("add"):
            today = datetime.today().strftime("%Y-%m-%d")
            date = input(f"Date (YYYY-MM-DD) [{today}]: ").strip() or today
            # validate
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                print(" Invalid date format.")
                continue
            desc = input("Description: ").strip()
            cat = input(f"Category (or new): ").strip().lower()
            amount_s = input("Amount (e.g., 12.50): ").strip()
            try:
                amount = round(float(amount_s), 2)
            except Exception:
                print(" Amount must be numeric.")
                continue
            add_expense(date, desc, cat, amount)
            continue
        if cmd.startswith("list"):
            parts = cmd.split()
            limit = None
            if len(parts) == 2 and parts[1].isdigit():
                limit = int(parts[1])
            list_expenses(limit)
            continue
        if cmd == "summary":
            category_summary()
            continue
        if cmd.startswith("monthly"):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: monthly YYYY-MM")
                continue
            monthly_summary(parts[1])
            continue
        if cmd == "categories":
            list_categories()
            continue
        if cmd.startswith("delete"):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("Usage: delete N")
                continue
            delete_expense(int(parts[1]))
            continue
        print(" Unknown command. Type 'help' for a list of commands.")

def main():
    # Simple argparse-like dispatch without importing argparse to keep it minimal
    args = sys.argv[1:]
    if not args:
        # no args -> interactive mode
        interactive()
        return

    cmd = args[0]
    if cmd == "add" and len(args) >= 5:
        # budget add YYYY-MM-DD "desc" category amount
        date = valid_date(args[1])
        desc = args[2]
        category = args[3].lower()
        amount = parse_amount(args[4])
        add_expense(date, desc, category, amount)
    elif cmd == "list":
        limit = int(args[1]) if len(args) == 2 and args[1].isdigit() else None
        list_expenses(limit)
    elif cmd == "summary":
        category_summary()
    elif cmd == "monthly" and len(args) == 2:
        monthly_summary(args[1])
    elif cmd == "categories":
        list_categories()
    elif cmd == "delete" and len(args) == 2:
        delete_expense(int(args[1]))
    else:
        print("""Usage:
  python budget_tracker.py                # interactive mode
  python budget_tracker.py add YYYY-MM-DD "desc" category amount
  python budget_tracker.py list [N]
  python budget_tracker.py summary
  python budget_tracker.py monthly YYYY-MM
  python budget_tracker.py categories
  python budget_tracker.py delete N
""")

if __name__ == "__main__":
    main()
