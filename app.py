import os
import logging
import pandas as pd
from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Flask setup
app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Categories for expense tracking
CATEGORIES = [
    'Tuition', 'Housing', 'Food', 'Transportation', 'Books_Supplies',
    'Entertainment', 'Personal_Care', 'Technology', 'Health_Wellness', 'Miscellaneous'
]

# Excel file path
DATA_FILE = os.path.join(os.getcwd(), 'data', 'student_spending.xlsx')

# Ensure Excel exists
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    df_init = pd.DataFrame(columns=['Date', 'Category', 'Amount'])
    df_init.to_excel(DATA_FILE, index=False)
    logger.debug("Created new Excel file at %s", DATA_FILE)

# ---------------- Gemini API setup ---------------- #
try:
    import google.generativeai as genai
    GEN_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
    genai.configure(api_key=GEN_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    logger.debug("Gemini API configured successfully")
except Exception as e:
    logger.error("Failed to configure Gemini API: %s", str(e))
    model = None
# -------------------------------------------------- #

def get_week_data():
    """Fetch previous and current week data for dashboard."""
    prev_dict = {cat: 0 for cat in CATEGORIES}
    curr_dict = {cat: 0 for cat in CATEGORIES}
    prev_total = curr_total = 0

    try:
        df = pd.read_excel(DATA_FILE)
        if df.empty:
            return prev_dict, curr_dict, prev_total, curr_total

        unique_dates = sorted(df['Date'].unique(), reverse=True)

        # Previous week = latest date in Excel
        if unique_dates:
            latest_date = unique_dates[0]
            latest_data = df[df['Date'] == latest_date]
            latest_group = latest_data.groupby('Category')['Amount'].sum().to_dict()
            for cat in CATEGORIES:
                prev_dict[cat] = round(latest_group.get(cat, 0), 2)
            prev_total = sum(prev_dict.values())

        # Current week = start fresh
        curr_dict = {cat: 0 for cat in CATEGORIES}
        curr_total = 0

    except Exception as e:
        logger.error("Error fetching data: %s", str(e))

    return prev_dict, curr_dict, prev_total, curr_total



# ------------------ Routes ------------------ #

@app.route("/", methods=["GET"])
def home():
    return render_template("about.html")


@app.route("/dashboard", methods=["GET"])
def dashboard():
    prev_dict, curr_dict, prev_total, curr_total = get_week_data()

    fin_health_score = 75
    challenges = ["No-Spend Day", "Cook at Home", "Save ₹500 this week"]
    total_expense = curr_total
    total_savings = max(0, 5000 - total_expense)
    prev_expenses_list = list(prev_dict.values())
    curr_expenses_list = list(curr_dict.values())
    challenge_labels = ["Challenge 1", "Challenge 2", "Challenge 3"]
    challenge_values = [3, 2, 4]

    return render_template(
        "index.html",
        categories=CATEGORIES,
        prev_expenses_dict=prev_dict,
        curr_expenses_dict=curr_dict,
        prev_total=prev_total,
        curr_total=curr_total,
        fin_health_score=fin_health_score,
        challenges=challenges,
        total_expense=total_expense,
        total_savings=total_savings,
        prev_expenses_list=prev_expenses_list,
        curr_expenses_list=curr_expenses_list,
        challenge_labels=challenge_labels,
        challenge_values=challenge_values
    )


@app.route("/chatbot", methods=["GET"])
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/log_expense", methods=["POST"])
def log_expense():
    try:
        data = request.get_json()
        date_today = datetime.now().strftime('%Y-%m-%d')

        # Voice input using Gemini AI suggestion
        if "text" in data and model:
            prompt = f"Interpret the user input '{data['text']}' as a category and amount from {CATEGORIES}."
            resp = model.generate_text(prompt=prompt)
            # Expecting format "Category Amount"
            text = resp.text.strip().split()
            if len(text) >= 2:
                category = text[0].capitalize()
                amount = float(text[1])
                if category in CATEGORIES:
                    df_new = pd.DataFrame([{'Date': date_today, 'Category': category, 'Amount': amount}])
                else:
                    return jsonify({"message": f"Unknown category {category}"}), 400
            else:
                return jsonify({"message": "Invalid voice input format"}), 400

        else:
            # Table input or fallback
            rows = [{'Date': date_today, 'Category': cat, 'Amount': float(amount)} for cat, amount in data.items()]
            df_new = pd.DataFrame(rows)

        # Read existing data
        df_existing = pd.read_excel(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame()
        if not df_existing.empty:
            df_existing = df_existing[df_existing['Date'] != date_today]

        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(DATA_FILE, index=False)

        return jsonify({"message": "Expense logged successfully"}), 200

    except Exception as e:
        logger.error("Error logging expense: %s", str(e))
        return jsonify({"message": "Error logging expense"}), 500


# ------------------ Run ------------------ #
if __name__ == "__main__":
    app.run(debug=True)

