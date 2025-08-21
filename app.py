from flask import Flask, render_template, request, jsonify
import pandas as pd
import re

app = Flask(__name__)

# --------- Load Historical Data ---------
df1 = pd.read_excel("data/student_spending1.xlsx")
df2 = pd.read_excel("data/student_spending2.xlsx")
df = pd.concat([df1, df2], ignore_index=True)

# Define expense categories
categories = ["tuition","housing","food","transportation","books_supplies",
              "entertainment","personal_care","technology","health_wellness","miscellaneous"]

# Ensure all expense columns are numeric
for cat in categories:
    df[cat] = pd.to_numeric(df[cat], errors='coerce').fillna(0)

# --------- Initialize Current Week Expenses ---------
current_expenses = {cat:0 for cat in categories}

# --------- Helper: Get Previous Week Expenses ---------
def get_last_week_expenses():
    if len(df) > 0:
        last_row = df.iloc[-1]
        last_week_expenses = {cat: last_row[cat] for cat in categories}
        return last_week_expenses
    else:
        return {cat:0 for cat in categories}

# --------- Financial Health Score Function ---------
def calculate_health_score(expenses, income, financial_aid=0):
    total_expense = sum(expenses.values())
    savings_ratio = max(0, income - total_expense) / income
    score = int(savings_ratio * 70)  # 70% weight
    
    # Financial aid contributes up to 10%
    aid_score = min(financial_aid / income * 100, 10)
    
    # Extra 20% for low spending categories (savings > 20% income)
    buffer_score = 20 if savings_ratio > 0.2 else 0
    
    final_score = min(100, score + aid_score + buffer_score)
    return final_score

# --------- Fun Gamified Challenges Function ---------
def generate_fun_challenges(expenses, income):
    challenges = []

    # Food / Dining challenge
    if expenses.get("food",0) > 0.2 * income:
        challenges.append("🎯 No Takeout Challenge – Try cooking at home for a week!")

    # Entertainment challenge
    if expenses.get("entertainment",0) > 500:
        challenges.append("💡 Movie-Free Weekend – Skip movies this weekend to save money!")

    # Technology / gadgets challenge
    if expenses.get("technology",0) > 300:
        challenges.append("🖥️ Tech Timeout – Avoid online shopping for gadgets for 1 week!")

    # Fun saving challenge if overall savings good
    total_expense = sum(expenses.values())
    if total_expense < 0.7 * income:
        challenges.append("🏆 Save & Treat – You’re saving well! Treat yourself within budget.")

    return challenges

# --------- Home Route ---------
@app.route("/", methods=["GET","POST"])
def home():
    user_input_given = False

    # Previous week
    previous_week_expenses = get_last_week_expenses()
    total_prev_week = sum(previous_week_expenses.values())
    
    # Copy previous week to current for default
    global current_expenses
    current_expenses = previous_week_expenses.copy()

    # Default income and aid from historical average
    weekly_income = df['monthly_income'].mean()
    financial_aid = df['financial_aid'].mean()

    if request.method == "POST":
        if request.form.get("use_input") == "yes":
            user_input_given = True
            income_val = request.form.get("monthly_income")
            aid_val = request.form.get("financial_aid")
            if income_val:
                weekly_income = float(income_val)
            if aid_val:
                financial_aid = float(aid_val)
            for cat in categories:
                val = request.form.get(cat)
                if val:
                    current_expenses[cat] = float(val)

    # Financial health score
    health_score = calculate_health_score(current_expenses, weekly_income, financial_aid)

    # Fun gamified challenges
    challenges = generate_fun_challenges(current_expenses, weekly_income)

    return render_template("index.html",
                           health_score=health_score,
                           mood_insights=[],
                           nudges=challenges,
                           expenses=current_expenses,
                           total_prev_week=total_prev_week,
                           user_input_given=user_input_given)

# --------- Voice Input Route ---------
@app.route("/log_expense", methods=["POST"])
def log_expense():
    data = request.get_json()
    text = data.get("text","").lower()
    amount = None
    category = None

    # Extract amount
    match = re.search(r'\d+(\.\d+)?', text)
    if match:
        amount = float(match.group())

    # Detect any category in text
    for cat in categories:
        if cat.replace("_"," ") in text:
            category = cat
            break

    # Error handling
    if not category:
        return jsonify({"message": "No valid expense category detected. Mention one of: " + ", ".join([c.replace('_',' ') for c in categories])})
    if not amount:
        return jsonify({"message": "No amount detected. Please say a number for your expense."})

    # Update current expenses
    current_expenses[category] += amount
    return jsonify({"message": f"Logged ₹{amount} to {category.replace('_',' ')}!"})

if __name__ == "__main__":
    app.run(debug=True)
