from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# ---------------- Step 1: Load historical weekly data ----------------
df1 = pd.read_excel("data/student_spending1.xlsx")
df2 = pd.read_excel("data/student_spending2.xlsx")
df = pd.concat([df1, df2], ignore_index=True)

# List of expense categories
categories = df.columns[2:].tolist()  # skip monthly_income and financial_aid

# ---------------- Helper functions ----------------
def calculate_financial_health(expenses, income, financial_aid):
    """
    Weekly Financial Health Score (0-100)
    - Based on total weekly spending vs income + aid
    - Balanced spending across categories
    """
    total_expense = sum(expenses.values())
    total_income = income + financial_aid
    savings_ratio = max(0, (total_income - total_expense) / total_income)
    
    category_std = pd.Series(expenses).std()
    balanced_score = max(0, 1 - category_std / (total_expense + 1e-5))  # prevent div by zero
    
    score = int((savings_ratio * 70) + (balanced_score * 30))
    return min(max(score, 0), 100)

def generate_expense_mood_linker(expenses):
    insights = []
    for cat, amt in expenses.items():
        if amt > 1000:
            insights.append(f"High spending on {cat} may relate to your mood. Observe patterns!")
    return insights

def generate_financial_nudges(expenses):
    nudges = []
    for cat, amt in expenses.items():
        if amt > 1500:
            nudges.append(f"Try reducing {cat} spending by 10% this week to save more!")
    return nudges

# ---------------- Flask Routes ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    # Default: average of weekly history
    historical_avg = df[categories].mean().to_dict()
    avg_income = df['monthly_income'].mean()
    avg_financial_aid = df['financial_aid'].mean()

    # Default display: historical averages
    display_expenses = historical_avg.copy()

    # Current user input (empty by default)
    current_expenses = {cat: 0 for cat in categories}
    income = avg_income
    financial_aid = avg_financial_aid
    user_input_given = False

    if request.method == "POST":
        if request.form.get("use_input") == "yes":
            user_input_given = True
            # Read only entered fields; missing fields default to 0
            for cat in categories:
                value = request.form.get(cat)
                current_expenses[cat] = float(value) if value else 0
            income_input = request.form.get("monthly_income")
            aid_input = request.form.get("financial_aid")
            income = float(income_input) if income_input else avg_income
            financial_aid = float(aid_input) if aid_input else avg_financial_aid
            display_expenses = current_expenses  # show user input in table

    # Calculate features based on current input or historical average
    health_score = calculate_financial_health(display_expenses, income, financial_aid)
    mood_insights = generate_expense_mood_linker(display_expenses)
    nudges = generate_financial_nudges(display_expenses)

    return render_template(
        "index.html",
        expenses=display_expenses,
        health_score=health_score,
        mood_insights=mood_insights,
        nudges=nudges,
        user_input_given=user_input_given
    )

if __name__ == "__main__":
    app.run(debug=True)
