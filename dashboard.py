import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import plotly.express as px
import shutil
import csv
import json
from utils.constants import EXPENSE_CATEGORIES, INCOME_CATEGORIES

# --- File Paths ---
TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"
BACKUPS_DIR = "backups"

# --- App Styling ---
def apply_styling():
    st.set_page_config(layout="wide", page_title="Finance Tracker", page_icon="🪙")
    custom_css = """
    <style>
        /* Main font and background */
        body {
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            background-color: #F0F2F6;
        }

        /* Sidebar styling */
        .css-1d391kg {
            background-color: #FFFFFF;
            border-right: 1px solid #E6E9EF;
        }

        /* Metric card styling - FIX */
        .stMetric {
            background-color: #FFFFFF;
            border: 1px solid #E6E9EF;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.04);
            color: #31333F; /* Set a default dark color for all text within the metric */
        }
        
        /* Explicitly target the metric label and value to ensure they are dark */
        [data-testid="stMetricLabel"] > div {
            color: #5E6278;
        }
        
        [data-testid="stMetricValue"] {
            color: #181C32;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 1.1rem;
            font-weight: 600;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# --- Helper Functions ---
def load_transactions():
    if not os.path.exists(TRANSACTIONS_FILE):
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])
    transactions = []
    with open(TRANSACTIONS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(',', 4)
            if len(parts) == 5:
                date_str, type, category, amount_paisa, description = parts
                transactions.append({
                    "Date": datetime.strptime(date_str, "%Y-%m-%d"),
                    "Type": type, "Category": category, 
                    "Amount": int(amount_paisa) / 100, "Description": description
                })
    return pd.DataFrame(transactions)

def load_budgets():
    if not os.path.exists(BUDGETS_FILE): return {}
    budgets = {}
    with open(BUDGETS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(',', 1)
            if len(parts) == 2: budgets[parts[0]] = int(parts[1]) / 100
    return budgets

def add_transaction_to_file(date_str, type, category, amount_paisa, description):
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(f"{date_str},{type},{category},{amount_paisa},{description}\n")

def set_budget_to_file(category, budget_amount_paisa):
    budgets = load_budgets()
    budgets[category] = budget_amount_paisa / 100
    with open(BUDGETS_FILE, "w") as f:
        for cat, amount in budgets.items():
            f.write(f"{cat},{int(amount * 100)}\n")

# --- Page Rendering Functions ---

def render_main_dashboard():
    st.title("📊 Financial Overview")
    st.markdown("---")

    transactions_df = load_transactions()
    budgets_data = load_budgets()

    current_month_str = datetime.now().strftime("%B %Y")
    current_month_df = transactions_df[transactions_df['Date'].dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]

    st.header(f"Summary for {current_month_str}")
    total_income = current_month_df[current_month_df['Type'] == 'income']['Amount'].sum()
    total_expenses = current_month_df[current_month_df['Type'] == 'expense']['Amount'].sum()
    balance = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{total_income:,.2f}", help="Sum of all income in the current month.")
    col2.metric("Total Expenses", f"₹{total_expenses:,.2f}", help="Sum of all expenses in the current month.")
    col3.metric("Net Balance", f"₹{balance:,.2f}", delta=f"{balance:,.2f}", delta_color="normal" if balance > 0 else "inverse")

    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Budget Status")
        if budgets_data:
            for category, budgeted_amount in budgets_data.items():
                spent_amount = current_month_df[(current_month_df['Type'] == 'expense') & (current_month_df['Category'] == category)]['Amount'].sum()
                percentage_used = (spent_amount / budgeted_amount * 100) if budgeted_amount > 0 else 0
                st.markdown(f"**{category}**")
                st.progress(min(int(percentage_used), 100), text=f"Spent: ₹{spent_amount:,.2f} / Budget: ₹{budgeted_amount:,.2f}")
        else:
            st.info("No budgets set. Use the 'Add New Data' page to set them.")

    with c2:
        st.subheader("Recent Transactions")
        st.dataframe(transactions_df.sort_values(by='Date', ascending=False).head(10), use_container_width=True)

def render_transactions_page():
    st.title("🧾 View & Filter Transactions")
    transactions_df = load_transactions()
    if transactions_df.empty:
        st.warning("No transactions recorded yet. Add some from the 'Add New Data' page.")
        return

    with st.sidebar:
        st.header("Filter Options")
        min_date, max_date = transactions_df['Date'].min().date(), transactions_df['Date'].max().date()
        start_date = st.date_input("Start date", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("End date", max_date, min_value=min_date, max_value=max_date)
        transaction_type = st.multiselect("Type", options=transactions_df['Type'].unique(), default=transactions_df['Type'].unique())
        selected_categories = st.multiselect("Category", options=sorted(transactions_df['Category'].unique()), default=sorted(transactions_df['Category'].unique()))

    filtered_df = transactions_df[(transactions_df['Date'].dt.date >= start_date) & (transactions_df['Date'].dt.date <= end_date) & (transactions_df['Type'].isin(transaction_type)) & (transactions_df['Category'].isin(selected_categories))]
    
    st.metric("Total Amount in Filter", f"₹{filtered_df['Amount'].sum():,.2f}")
    st.data_editor(filtered_df.sort_values(by="Date", ascending=False), use_container_width=True, hide_index=True, column_config={"Date": st.column_config.DateColumn(format="YYYY-MM-DD"), "Amount": st.column_config.NumberColumn(format="₹ %.2f")})

def render_analytics_page():
    st.title("📈 Financial Analytics")
    transactions_df = load_transactions()
    if transactions_df.empty:
        st.warning("No transactions recorded yet. Analytics requires data."); return

    transactions_df['Month'] = transactions_df['Date'].dt.to_period('M').astype(str)
    all_months = sorted(transactions_df['Month'].unique(), reverse=True)
    selected_month = st.selectbox("Select Month to Analyze", all_months)
    month_df = transactions_df[transactions_df['Month'] == selected_month]

    total_income = month_df[month_df['Type'] == 'income']['Amount'].sum()
    total_expenses = month_df[month_df['Type'] == 'expense']['Amount'].sum()
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0

    st.header(f"Summary for {selected_month}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Income", f"₹{total_income:,.2f}"); c2.metric("Total Expenses", f"₹{total_expenses:,.2f}"); c3.metric("Net Savings", f"₹{net_savings:,.2f}"); c4.metric("Savings Rate", f"{savings_rate:.1f}%")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Spending by Category")
        expense_df = month_df[month_df['Type'] == 'expense']
        if not expense_df.empty:
            fig = px.pie(expense_df, names='Category', values='Amount', hole=.3, title="Spending Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No expenses this month.")
    with c2:
        st.subheader("Income by Source")
        income_df = month_df[month_df['Type'] == 'income']
        if not income_df.empty:
            income_by_source = income_df.groupby('Category')['Amount'].sum().reset_index()
            fig = px.bar(income_by_source, x='Category', y='Amount', title="Income Sources")
            st.plotly_chart(fig, use_container_width=True)
        else: st.info("No income this month.")
            
    st.subheader("Income vs. Expense Trend")
    trend_df = transactions_df.groupby(['Month', 'Type'])['Amount'].sum().unstack().fillna(0).reset_index()
    if 'income' not in trend_df: trend_df['income'] = 0
    if 'expense' not in trend_df: trend_df['expense'] = 0
    trend_df['savings'] = trend_df['income'] - trend_df['expense']
    fig = px.line(trend_df, x='Month', y=['income', 'expense', 'savings'], title='Monthly Trends', markers=True)
    st.plotly_chart(fig, use_container_width=True)

def render_data_management_page():
    st.title("💾 Data Management")
    with st.expander("Export Transactions", expanded=True):
        transactions_df = load_transactions()
        if transactions_df.empty: st.info("No transactions to export.")
        else:
            c1, c2 = st.columns(2)
            export_format = c1.radio("Export Format", ["CSV", "JSON"])
            data = transactions_df.to_csv(index=False).encode('utf-8') if export_format == "CSV" else transactions_df.to_json(orient='records', indent=4).encode('utf-8')
            file_extension = "csv" if export_format == "CSV" else "json"
            c2.download_button(f"Download as {export_format}", data, f"export_{datetime.now().strftime('%Y-%m-%d')}.{file_extension}", f'text/{file_extension}', use_container_width=True)

    with st.expander("Import Transactions"):
        uploaded_file = st.file_uploader("Upload a CSV or JSON file", type=['csv', 'json'])
        if uploaded_file and st.button("Import File", use_container_width=True):
            try:
                with open(TRANSACTIONS_FILE, "r") as f: existing_lines = {line.strip() for line in f.readlines()}
            except FileNotFoundError: existing_lines = set()
            string_data = uploaded_file.getvalue().decode('utf-8')
            new_transactions = list(csv.DictReader(string_data.splitlines())) if uploaded_file.name.lower().endswith('.csv') else json.loads(string_data)
            added_count, skipped_count = 0, 0
            with open(TRANSACTIONS_FILE, "a") as f:
                for t in new_transactions:
                    try:
                        datetime.strptime(t['date'], "%Y-%m-%d")
                        amount = int(t['amount_paisa'])
                        if amount <= 0: raise ValueError("Amount must be positive")
                        line_to_add = f"{t['date']},{t['type']},{t['category']},{amount},{t['description']}"
                        if line_to_add in existing_lines: skipped_count += 1
                        else:
                            f.write(line_to_add + "\n")
                            existing_lines.add(line_to_add)
                            added_count += 1
                    except (KeyError, ValueError): skipped_count += 1
            st.success(f"Import complete! Added: {added_count}, Skipped: {skipped_count}")

    with st.expander("Backup & Restore"):
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        st.subheader("Create Backup")
        if st.button("Create New Backup", use_container_width=True):
            backup_filename = os.path.join(BACKUPS_DIR, f"backup-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
            shutil.make_archive(backup_filename, 'zip', 'database')
            st.success(f"Backup '{backup_filename}.zip' created!")

        st.subheader("Restore from Backup")
        backups = sorted([f for f in os.listdir(BACKUPS_DIR) if f.endswith('.zip')], reverse=True)
        if not backups: st.info("No backups found.")
        else:
            backup_choice = st.selectbox("Select a backup", backups)
            if st.checkbox("I understand this will overwrite all current data."):
                if st.button("Restore", type="primary", use_container_width=True):
                    shutil.unpack_archive(os.path.join(BACKUPS_DIR, backup_choice), '.', 'zip')
                    st.success(f"Restored from {backup_choice}. Please refresh.")

def render_smart_assistant_page():
    st.title("💡 Smart Financial Assistant")
    transactions_df = load_transactions()
    if transactions_df.empty:
        st.warning("No transactions recorded yet."); return
        
    budgets = load_budgets()
    now = datetime.now()
    current_month_df = transactions_df[transactions_df['Date'].dt.strftime("%Y-%m") == now.strftime("%Y-%m")]

    with st.container(border=True):
        st.subheader("Spending Insights")
        expense_df = current_month_df[current_month_df['Type'] == 'expense']
        if not expense_df.empty:
            top_category = expense_df.groupby('Category')['Amount'].sum().idxmax()
            top_amount = expense_df.groupby('Category')['Amount'].sum().max()
            st.write(f"Your top spending category this month is **{top_category}** with **₹{top_amount:,.2f}**.")
            if top_category == 'Food': st.info("💡 **Tip:** Consider planning meals for the week or looking for deals at grocery stores.")
            elif top_category == 'Shopping': st.info("💡 **Tip:** Try a 'no-spend' challenge or unsubscribe from marketing emails.")
            
            large_expenses = expense_df[expense_df['Amount'] > expense_df['Amount'].sum() * 0.25]
            if not large_expenses.empty:
                for _, row in large_expenses.iterrows(): st.warning(f"**Alert:** An expense of **₹{row['Amount']:,.2f}** for '{row['Description']}' seems high.")
        else: st.write("No expenses this month to analyze.")

    with st.container(border=True):
        st.subheader("Savings & Budget Tips")
        three_months_ago = now - relativedelta(months=3)
        recent_income = transactions_df[(transactions_df['Type'] == 'income') & (transactions_df['Date'] >= three_months_ago)]['Amount'].sum()
        avg_monthly_income = recent_income / 3 if recent_income > 0 else 0
        if avg_monthly_income > 0: st.write(f"Based on average income, a good monthly savings target is **₹{(avg_monthly_income * 0.15):,.2f}** (15%).")
        
        if budgets:
            all_good = True
            for category, budget_amount in budgets.items():
                spent = expense_df[expense_df['Category'] == category]['Amount'].sum()
                if spent > budget_amount:
                    st.error(f"**Over budget!** You've spent **₹{(spent - budget_amount):,.2f}** too much in '{category}'.")
                    all_good = False
                elif spent > budget_amount * 0.8:
                    st.warning(f"**Nearing limit!** Only **₹{(budget_amount - spent):,.2f}** left in '{category}'.")
                    all_good = False
            if all_good: st.success("You are staying within all your budget limits. Keep it up!")
        else: st.info("Set some budgets in the 'Add New Data' page to better control your spending.")

def render_add_data_page():
    st.title("➕ Add New Data")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("Add New Transaction")
            with st.form("add_transaction_form", clear_on_submit=True):
                trans_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
                c1f, c2f = st.columns(2)
                amount = c1f.number_input("Amount", min_value=0.01, format="%.2f")
                category = c2f.selectbox("Category", EXPENSE_CATEGORIES if trans_type == "Expense" else INCOME_CATEGORIES)
                description = st.text_input("Description")
                date = st.date_input("Date", datetime.now())
                if st.form_submit_button("Add Transaction", use_container_width=True, type="primary"):
                    add_transaction_to_file(date.strftime("%Y-%m-%d"), trans_type.lower(), category, int(amount * 100), description)
                    st.success(f"{trans_type} of ₹{amount:,.2f} added!")
    with c2:
        with st.container(border=True):
            st.subheader("Set Monthly Budget")
            with st.form("set_budget_form", clear_on_submit=True):
                c1b, c2b = st.columns(2)
                category = c1b.selectbox("Category", EXPENSE_CATEGORIES, key="budget_cat")
                amount = c2b.number_input("Budget Amount", min_value=0.01, format="%.2f", key="budget_amt")
                if st.form_submit_button("Set Budget", use_container_width=True):
                    set_budget_to_file(category, int(amount * 100))
                    st.success(f"Budget for {category} set to ₹{amount:,.2f}")

# --- Main App ---
def main():
    apply_styling()
    
    with st.sidebar:
        st.title("🪙 Finance Tracker")
        page_selection = st.radio("Navigation", ["Dashboard", "Transactions", "Analytics", "Data Management", "Smart Assistant", "Add New Data"], label_visibility="collapsed")
        st.markdown("---")
        st.info("Built by a Gemini agent.")

    page_map = {
        "Dashboard": render_main_dashboard, "Transactions": render_transactions_page,
        "Analytics": render_analytics_page, "Data Management": render_data_management_page,
        "Smart Assistant": render_smart_assistant_page, "Add New Data": render_add_data_page,
    }
    
    if page_selection in page_map:
        page_map[page_selection]()

if __name__ == "__main__":
    main()
