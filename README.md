# 💸 Budget Tracker CLI

A simple, beginner-friendly command‑line app to track expenses to a CSV file.

## Features
- Add expenses with date, description, category, amount
- List all expenses (or the last N)
- Category summary totals
- Monthly breakdown (`YYYY-MM`)
- Delete by index
- CSV stored locally (`expenses.csv`)

## Quickstart
```bash
# 1) Open this folder in your terminal
cd budget_tracker_cli

# 2) Run interactively
python budget_tracker.py

# OR use commands
python budget_tracker.py add 2025-09-20 "Coffee" food 3.50
python budget_tracker.py list
python budget_tracker.py summary
python budget_tracker.py monthly 2025-09
python budget_tracker.py delete 3
```

## CSV Schema
`date, description, category, amount`

## Notes
- No external libraries required (pure Python standard library).
- You can change default categories by editing `CATEGORIES` in the code.