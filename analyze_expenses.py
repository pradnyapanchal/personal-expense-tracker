"""
PERSONAL EXPENSE TRACKER & VISUALIZER
======================================
A beginner-friendly Python project that reads your spending data from a
file and draws 4 charts with matplotlib so you can SEE where your money
goes.

HOW THIS IS "DYNAMIC":
-----------------------
You do NOT edit this script to change the results. You edit the DATA
FILE instead (expenses.csv, or swap in expenses.json / expenses.xlsx).
Add a row, change an amount, add a new category -> run the script again
-> every number and every chart updates automatically.

That's the whole story to tell in an interview:
"The data and the code are separate. Anyone can update the numbers
 without touching a single line of Python."

HOW TO RUN:
-----------
    python analyze_expenses.py
        -> looks for expenses.csv, then expenses.json, then expenses.xlsx
           in this same folder, and uses whichever one it finds first.

    python analyze_expenses.py my_other_file.xlsx
        -> or just tell it exactly which file to use.

WHAT YOUR DATA FILE NEEDS:
---------------------------
Just 3 columns (any of these common alternate names also work):
    date      (or: day, expense_date)
    category  (or: type, expense_category)
    amount    (or: expense, cost, price)
"""

import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


# =====================================================================
# STEP 1: FIND AND LOAD THE DATA FILE
# =====================================================================

def load_data(filepath):
    """Read the file into a pandas table (DataFrame), based on its extension."""
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath)
    elif filepath.endswith(".json"):
        return pd.read_json(filepath)
    elif filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Unsupported file type. Please use .csv, .json, or .xlsx")


def find_data_file():
    """If the user didn't specify a file, look for a default one in this folder."""
    for name in ["expenses.csv", "expenses.json", "expenses.xlsx"]:
        if os.path.exists(name):
            return name
    raise FileNotFoundError(
        "No expenses.csv / expenses.json / expenses.xlsx found in this folder. "
        "Add one of those files here, or run: python analyze_expenses.py <your_file>"
    )


# Use the file passed on the command line, OR auto-detect the default one
if len(sys.argv) > 1:
    data_file = sys.argv[1]
else:
    data_file = find_data_file()

print(f"Loading data from: {data_file}")
df = load_data(data_file)


# =====================================================================
# STEP 2: CLEAN UP THE DATA
# (so small differences in column naming don't break the script)
# =====================================================================

df.columns = [c.strip().lower() for c in df.columns]

rename_map = {
    "expense": "amount", "cost": "amount", "price": "amount",
    "type": "category", "expense_category": "category",
    "day": "date", "expense_date": "date",
}
df = df.rename(columns=rename_map)

required_columns = ["date", "category", "amount"]
for col in required_columns:
    if col not in df.columns:
        raise ValueError(f"Your data file is missing a required column: '{col}'")

df["date"] = pd.to_datetime(df["date"])
df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)


# =====================================================================
# STEP 3: CALCULATE SIMPLE SUMMARY NUMBERS
# =====================================================================

total_spent = df["amount"].sum()
avg_expense = df["amount"].mean()
num_expenses = len(df)
top_category = df.groupby("category")["amount"].sum().idxmax()

print("\n--- SUMMARY ---")
print(f"Total spent:        Rs. {total_spent:,.2f}")
print(f"Number of expenses: {num_expenses}")
print(f"Average expense:    Rs. {avg_expense:,.2f}")
print(f"Top category:       {top_category}")


# =====================================================================
# STEP 4: DRAW 4 CHARTS WITH MATPLOTLIB
# =====================================================================

fig, axes = plt.subplots(2, 2, figsize=(12, 9))
fig.suptitle("Personal Expense Dashboard", fontsize=16, fontweight="bold")

# --- Chart 1: Pie chart - how spending splits across categories ---
category_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
axes[0, 0].pie(category_totals, labels=category_totals.index, autopct="%1.1f%%", startangle=90)
axes[0, 0].set_title("Spending by Category (%)")

# --- Chart 2: Bar chart - same info, but easier to compare exact amounts ---
axes[0, 1].bar(category_totals.index, category_totals.values, color="steelblue")
axes[0, 1].set_title("Total Spent per Category")
axes[0, 1].set_ylabel("Amount (Rs.)")
axes[0, 1].tick_params(axis="x", rotation=45)

# --- Chart 3: Line chart - spending trend over time ---
daily_totals = df.groupby("date")["amount"].sum().sort_index()
axes[1, 0].plot(daily_totals.index, daily_totals.values, marker="o", color="darkorange")
axes[1, 0].set_title("Spending Over Time")
axes[1, 0].set_ylabel("Amount (Rs.)")
axes[1, 0].tick_params(axis="x", rotation=45)

# --- Chart 4: Horizontal bar chart - your 5 single biggest expenses ---
top5 = df.sort_values("amount", ascending=False).head(5)
labels = top5["category"] + " (" + top5["date"].dt.strftime("%b %d") + ")"
axes[1, 1].barh(labels, top5["amount"], color="crimson")
axes[1, 1].set_title("Top 5 Biggest Single Expenses")
axes[1, 1].set_xlabel("Amount (Rs.)")
axes[1, 1].invert_yaxis()  # biggest expense at the top

plt.tight_layout(rect=[0, 0, 1, 0.96])

output_file = "expense_charts.png"
plt.savefig(output_file, dpi=150)
print(f"\nCharts saved as an image to: {output_file}")

plt.show()
