# FinSync - AI-Powered Student Financial Management App

Finvoice is a lightweight financial management and advisory web application designed for students. It helps users track expenses, monitor financial health, gain behavioral insights, and receive gamified nudges to improve savings.

---

## **FinSync Folder Structure**
```
FinSync/                     # Root project folder
│
├── app.py                   # Main Flask application (backend logic)
│
├── data/                    # Excel datasets
│   ├── student_spending1.xlsx
│   └── student_spending2.xlsx
│
├── static/                  # Static files (CSS, images)
│   ├── styles.css           # Main CSS stylesheet
│   └── images/              # Images used in the app
│       ├── speechtext.jpg
│       └── student_finance.jpg
│
├── templates/               # HTML templates (frontend)
│   ├── index.html           # Dashboard page
│   ├── about.html           # About page
│   └── chatbot.html         # AI chatbot interface
│
└── README.md                # Project documentation
```

---

## **📄 Project Description**

FinSync allows students to:  
- Log and categorize expenses manually or via voice.  
- Monitor **Financial Health Score** (0–100).  
- Receive behavioral insights by linking spending to moods.  
- Get gamified nudges and challenges to save money.  
- Access a **chatbot** for personalized financial guidance.

---

## **Features**

1. **Financial Health Score**
   - Calculates a score (0–100) based on income, spending habits, savings ratio, and debt levels.
   - Gamifies financial wellness for students.

2. **Expense Logger**
   - Log new expenses by category, amount, and mood.
   - Supports mood-linked insights to understand emotional spending patterns.

3. **Financial Nudges & Challenges**
   - Provides actionable challenges like “Reduce spending in X category by 10%”.
   - Makes finance fun and less stressful.

4. **Dashboard**
   - Displays latest expense, savings, and financial health score.
   - Easy-to-use web interface with separate CSS styling.

- **Financial Health Score:** Gamified score (0–100) for financial wellness.  
- **Expense Logger:** Manual & voice input with mood tagging.  
- **Financial Nudges & Challenges:** Gamified savings prompts.  
- **Dashboard:** Displays totals, savings, and charts using Chart.js.  
- **AI Chatbot:** Personalized advisory integrated with Google Gemini API.  
---

## **🛠 Technology Stack**

### **Backend**
- Python – Logic, calculations, and data handling.  
- Flask – Routes and template rendering (`/`, `/about`, `/log_expense`, `/chatbot`).  
- Pandas – Read and process Excel files (`student_spending1.xlsx`, `student_spending2.xlsx`).  
- OS module – File path handling.  
- Random module – Generate dummy data for charts.

### **Frontend**
- HTML – Page structure (`index.html`, `about.html`, `chatbot.html`).  
- CSS – Styling (`styles.css`) and responsive dashboard.  
- JavaScript – Dynamic functionality:
  - Updating totals dynamically
  - AJAX form submissions
  - Voice input using Web Speech API
- Chart.js – Interactive charts: Expenses vs Savings, Weekly Comparison, Challenge Streaks.

### **Data**
- Excel files (.xlsx) – Stores historical and current week expenses.  
- JSON – Transmit data between frontend & backend.

### **Browser Features**
- Web Speech API – `webkitSpeechRecognition` for voice input.  
- Jinja2 – Embedded Python in HTML for dynamic content rendering.

### **AI Integration**
- Google Gemini API – Chatbot for personal financial advisory.

---

## **⚡ Installation & Setup**

1. **Clone the repository**:
```bash
git clone <your-repo-url>
cd FinSync


