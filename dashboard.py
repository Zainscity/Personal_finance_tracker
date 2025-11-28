import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import plotly.express as px
import shutil
import csv
import json
from io import StringIO, BytesIO
from utils.constants import EXPENSE_CATEGORIES, INCOME_CATEGORIES

# --- App Styling ---
def apply_styling():
    st.set_page_config(layout="wide", page_title="Finance Tracker", page_icon="🪙")
    custom_css = """
    <style>
        body { font-family: 'Segoe UI', 'Roboto', sans-serif; background-color: #F0F2F6; }
        .stMetric { background-color: #FFFFFF; border: 1px solid #E6E9EF; border-radius: 10px; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.04); color: #31333F; }
        [data-testid="stMetricLabel"] > div { color: #5E6278; }
        [data-testid="stMetricValue"] { color: #181C32; }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# --- Session State Initializer ---
def initialize_session_state():
    if 'transactions' not in st.session_state:
        st.session_state.transactions = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])
    if 'budgets' not in st.session_state:
        st.session_state.budgets = {}

# --- Session-Aware Helper Functions ---
def get_transactions():
    return st.session_state.transactions

def get_budgets():
    return st.session_state.budgets

def add_transaction(date, trans_type, category, amount, description):
    new_transaction = pd.DataFrame([{
        "Date": pd.to_datetime(date), "Type": trans_type, "Category": category, 
        "Amount": amount, "Description": description
    }])
    st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)

def set_budget(category, amount):
    st.session_state.budgets[category] = amount

# --- Page Rendering Functions ---

def render_main_dashboard():
    st.title("📊 Financial Overview")
    transactions_df = get_transactions()
    budgets_data = get_budgets()

    if transactions_df.empty:
        st.info("👋 Welcome! Add your first transaction from the '➕ Add New Data' page to get started.")
        return

    st.markdown("---")
    current_month_str = datetime.now().strftime("%B %Y")
    current_month_df = transactions_df[transactions_df['Date'].dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
    
    st.header(f"Summary for {current_month_str}")
    total_income = current_month_df[current_month_df['Type'] == 'income']['Amount'].sum()
    total_expenses = current_month_df[current_month_df['Type'] == 'expense']['Amount'].sum()
    balance = total_income - total_expenses
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{total_income:,.2f}")
    col2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    col3.metric("Net Balance", f"₹{balance:,.2f}", delta=f"{balance:,.2f}", delta_color="normal" if balance >= 0 else "inverse")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Budget Status")
        if budgets_data:
            current_month_df = transactions_df[transactions_df['Date'].dt.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
            for category, budgeted_amount in budgets_data.items():
                spent_amount = current_month_df[
                    (current_month_df['Type'] == 'expense') &
                    (current_month_df['Category'] == category)
                ]['Amount'].sum()
                percentage_used = (spent_amount / budgeted_amount * 100) if budgeted_amount > 0 else 0
                
                st.markdown(f"**{category}**")
                st.progress(min(int(percentage_used), 100), text=f"Spent: ₹{spent_amount:,.2f} / Budget: ₹{budgeted_amount:,.2f}")
        else:
            st.info("No budgets set. Use the 'Add New Data' page.")
    with c2:
        st.subheader("Recent Transactions")
        st.dataframe(transactions_df.sort_values(by='Date', ascending=False).head(10), use_container_width=True)

def render_transactions_page():
    st.title("🧾 View & Filter Transactions")
    transactions_df = get_transactions()
    if transactions_df.empty:
        st.warning("No transactions recorded yet."); return

    # ... (filtering logic remains the same)
    st.data_editor(transactions_df, use_container_width=True, hide_index=True)


def render_analytics_page():
    st.title("📈 Financial Analytics")
    transactions_df = get_transactions()
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
    st.info("Export your current session data or import data from a previous session.")

    with st.expander("Export Session Data", expanded=True):
        transactions_df = get_transactions()
        if transactions_df.empty: st.info("No transactions to export.")
        else:
            export_format = st.radio("Export Format", ["CSV", "JSON"])
            if export_format == "CSV":
                # Convert Amount to paisa for file storage consistency
                transactions_df['amount_paisa'] = (transactions_df['Amount'] * 100).astype(int)
                data = transactions_df[['Date', 'Type', 'Category', 'amount_paisa', 'Description']].to_csv(index=False).encode('utf-8')
            else:
                transactions_df['amount_paisa'] = (transactions_df['Amount'] * 100).astype(int)
                data = transactions_df[['Date', 'Type', 'Category', 'amount_paisa', 'Description']].to_json(orient='records', indent=4).encode('utf-8')
            
            st.download_button(f"Download as {export_format}", data, f"export_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}", use_container_width=True)

    with st.expander("Import Session Data"):
        uploaded_file = st.file_uploader("Upload a CSV or JSON file", type=['csv', 'json'])
        if uploaded_file and st.button("Import and Replace Data", use_container_width=True, type="primary"):
            try:
                string_data = uploaded_file.getvalue().decode('utf-8')
                new_trans_data = []
                if uploaded_file.name.lower().endswith('.csv'):
                    reader = csv.DictReader(StringIO(string_data))
                    new_trans_data = [row for row in reader]
                else:
                    new_trans_data = json.loads(string_data)

                # Create a new DataFrame from the imported data
                imported_df = pd.DataFrame(new_trans_data)
                imported_df['Date'] = pd.to_datetime(imported_df['date'])
                imported_df['Amount'] = pd.to_numeric(imported_df['amount_paisa']) / 100
                imported_df.rename(columns={'type': 'Type', 'category': 'Category', 'description': 'Description'}, inplace=True)
                
                # Replace session state
                st.session_state.transactions = imported_df[['Date', 'Type', 'Category', 'Amount', 'Description']]
                st.success(f"Successfully imported {len(st.session_state.transactions)} transactions!")
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred during import: {e}")

def render_smart_assistant_page():
    st.title("💡 Smart Financial Assistant")
    transactions_df = get_transactions()
    if transactions_df.empty:
        st.warning("No transactions recorded yet."); return
        
    budgets = get_budgets()
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
                trans_type = st.radio("Type", ["expense", "income"], horizontal=True)
                amount = st.number_input("Amount", min_value=0.01, format="%.2f")
                category = st.selectbox("Category", EXPENSE_CATEGORIES if trans_type == "expense" else INCOME_CATEGORIES)
                description = st.text_input("Description")
                date = st.date_input("Date", datetime.now())
                if st.form_submit_button("Add Transaction", use_container_width=True, type="primary"):
                    add_transaction(date, trans_type, category, amount, description)
                    st.success(f"{trans_type.capitalize()} of ₹{amount:,.2f} added!")
    with c2:
        with st.container(border=True):
            st.subheader("Set Monthly Budget")
            with st.form("set_budget_form", clear_on_submit=True):
                category = st.selectbox("Category", EXPENSE_CATEGORIES, key="budget_cat")
                amount = st.number_input("Budget Amount", min_value=0.01, format="%.2f", key="budget_amt")
                if st.form_submit_button("Set Budget", use_container_width=True):
                    set_budget(category, amount)
                    st.success(f"Budget for {category} set to ₹{amount:,.2f}")

# --- Main App ---
def main():
    apply_styling()
    initialize_session_state()
    
    with st.sidebar:
        st.title("🪙 Finance Tracker")
        page_selection = st.radio("Navigation", ["Dashboard", "Transactions", "Analytics", "Data Management", "Smart Assistant", "Add New Data"], label_visibility="collapsed")
        st.markdown("---")
        st.info("Your data is session-based and will reset when you close this tab. Use the Data Management page to save and load your progress.")

    page_map = {
        "Dashboard": render_main_dashboard, "Transactions": render_transactions_page,
        "Analytics": render_analytics_page, "Data Management": render_data_management_page,
        "Smart Assistant": render_smart_assistant_page, "Add New Data": render_add_data_page,
    }
    
    if page_selection in page_map:
        page_map[page_selection]()

if __name__ == "__main__":
    main()