🌟 Personal Finance Tracker CLI
A Fintech-Inspired Command Line Application to Manage Your Money Smartly

A fully interactive CLI-based Personal Finance Tracker built in Python — featuring transaction management, budgets, analytics, alerts, smart recommendations, and even a Streamlit web dashboard.

This project was designed and developed using Gemini CLI, AI-assisted development, UV, Rich, and Questionary, following a structured 7-day learning roadmap.

🚀 Features
✅ 1. Track Income & Expenses

Add expenses (category, amount, date, description)

Add income (source, amount, date)

Rich table display with beautiful colors

Intelligent sorting and filtering

Accurate calculations (no floating-point errors!)

✅ 2. Monthly Budgets

Set per-category budgets

Track spending vs. budget

Utilization percentage

Progress bars with color indicators

Highlights overspending categories

✅ 3. Financial Analytics Engine

Monthly spending breakdown

Category-wise insights

Savings rate calculation

Burn rate analysis

Month-to-month comparison

Financial health score (0-100)

ASCII pie charts

✅ 4. Smart Assistant

Daily financial check

Smart recommendations

Overspending alerts

Large transaction warnings

Savings optimization suggestions

Goal tracking (emergency fund, vacation, etc.)

✅ 5. Data Management

Export transactions → CSV / JSON

Export monthly reports

Import CSV files

Automatic backups

Data validation & cleanup tools

✅ 6. Streamlit Web Dashboard

A clean, modern web UI to visualize:

Balance summary

Budget progress bars

Recent transactions

Category charts

🛠 Tech Stack
Tool	Purpose
Python 3.11+	Main language
UV	Package & environment manager
Gemini CLI	AI-powered coding
Questionary	Interactive CLI menus
Rich	Tables, colors, styling
Streamlit	Web dashboard
Plain text storage	No database needed
📁 Project Structure
finance-tracker/
├── main.py
├── GEMINI.md
├── database/
│   ├── transactions.txt
│   └── budgets.txt
├── features/
│   ├── transactions/
│   │   ├── GEMINI.md
│   │   └── transactions.py
│   ├── budget/
│   │   ├── GEMINI.md
│   │   └── budgets.py
│   ├── financial_analytics/
│   │   ├── GEMINI.md
│   │   └── analytics.py
│   ├── smart_assistant/
│   │   ├── GEMINI.md
│   │   └── assistant.py
│   └── data_management/
│       ├── GEMINI.md
│       └── data_manager.py
└── dashboard/
    └── app.py   (Streamlit)

⚙️ Installation
1. Clone Repository
git clone https://github.com/zainscity/Personal_finance_tracker
cd Personal_finance_tracker

2. Install UV
pip install uv
# or
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

3. Create Virtual Environment
uv venv
.venv/Scripts/activate   # Windows

4. Install Dependencies
uv add rich questionary streamlit

▶️ Running the CLI
python main.py


Main menu includes:

Add Expense

Add Income

View Transactions

Balance Overview

Budgets

Analytics

Smart Assistant

Export/Import

Backup Tools

🌐 Running the Web Dashboard
streamlit run dashboard/app.py

🧠 How This Project Was Built (7-Day Roadmap)

This project followed a structured learning challenge:

Day 1: Setup with Gemini CLI + UV

Day 2: Transactions

Day 3: Budgeting

Day 4: Analytics engine

Day 5: Smart recommendations

Day 6: Data export/import

Day 7: Streamlit dashboard

Great for learning:
✔ Python
✔ Fintech logic
✔ AI-assisted development
✔ CLI UX
✔ File-based databases
✔ Web dashboards

🤝 Contributing

Contributions and improvements are welcome!

Fork the repo

Create a feature branch

Submit a PR

📝 License

MIT License — free to use and modify.

⭐ Support The Project

If you found this helpful, kindly ⭐ star the repo on GitHub!