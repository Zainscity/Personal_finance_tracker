from datetime import datetime
from dateutil.relativedelta import relativedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from collections import defaultdict
import os

# File paths
TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"

# --- Helper Functions ---

def _load_transactions():
    """Loads all transactions from the file."""
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    transactions = []
    with open(TRANSACTIONS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(',', 4)
            if len(parts) == 5:
                date_str, type, category, amount_paisa, description = parts
                transactions.append({
                    "date": datetime.strptime(date_str, "%Y-%m-%d"),
                    "type": type,
                    "category": category,
                    "amount_paisa": int(amount_paisa),
                    "description": description
                })
    return transactions

def _load_budgets():
    """Loads all budgets from the file."""
    if not os.path.exists(BUDGETS_FILE):
        return {}
    budgets = {}
    with open(BUDGETS_FILE, "r") as f:
        for line in f:
            parts = line.strip().split(',', 1)
            if len(parts) == 2:
                cat, amount = parts
                budgets[cat] = int(amount)
    return budgets

def _get_trend_arrow(current, previous):
    """Returns a colored arrow indicating the trend."""
    if current > previous:
        return "[red]⬆️ Up[/red]"
    elif current < previous:
        return "[green]⬇️ Down[/green]"
    else:
        return "[blue]➡️ Stable[/blue]"

# --- Main Analytics Functions ---

def spending_analysis():
    """Performs and displays spending analysis for the current month vs. last month."""
    console = Console()
    transactions = _load_transactions()

    if not transactions:
        console.print("[bold yellow]No transactions found to analyze.[/bold yellow]")
        return

    now = datetime.now()
    current_month_start = now.replace(day=1)
    last_month_start = (current_month_start - relativedelta(months=1)).replace(day=1)
    
    current_month_expenses = [
        t for t in transactions 
        if t['type'] == 'expense' and t['date'] >= current_month_start
    ]
    last_month_expenses = [
        t for t in transactions 
        if t['type'] == 'expense' and last_month_start <= t['date'] < current_month_start
    ]

    total_current_month_expense = sum(t['amount_paisa'] for t in current_month_expenses)
    total_last_month_expense = sum(t['amount_paisa'] for t in last_month_expenses)

    console.print(Panel(f"[bold cyan]Spending Analysis: {now.strftime('%B %Y')}[/bold cyan]", expand=False))

    # Breakdown by category (current month)
    category_spending = defaultdict(int)
    for expense in current_month_expenses:
        category_spending[expense['category']] += expense['amount_paisa']

    if total_current_month_expense > 0:
        sorted_categories = sorted(category_spending.items(), key=lambda item: item[1], reverse=True)
        
        breakdown_text = ""
        for category, amount_paisa in sorted_categories:
            percentage = (amount_paisa / total_current_month_expense) * 100
            bar_length = int(percentage / 4)
            breakdown_text += f"{category.ljust(15)} {'█' * bar_length} {percentage:.1f}% ({amount_paisa/100:.2f})\n"
        
        console.print(Panel(breakdown_text.strip(), title="Spending Breakdown by Category", border_style="green"))

        # Top 3 categories
        top_categories_text = "\n".join([f"{i+1}. {cat}: {amt/100:.2f}" for i, (cat, amt) in enumerate(sorted_categories[:3])])
        console.print(Panel(top_categories_text, title="Top 3 Spending Categories", border_style="yellow"))
    else:
        console.print("[yellow]No spending recorded this month.[/yellow]")

    # Comparison
    avg_daily_expense = (total_current_month_expense / now.day) / 100 if now.day > 0 else 0
    trend = _get_trend_arrow(total_current_month_expense, total_last_month_expense)

    comparison_text = Text(f"Total This Month: {total_current_month_expense/100:.2f}\n"
                           f"Total Last Month: {total_last_month_expense/100:.2f}\n"
                           f"Trend: {trend}\n\n"
                           f"Average Daily Expense (Burn Rate): {avg_daily_expense:.2f}")
    console.print(Panel(comparison_text, title="Comparison & Burn Rate", border_style="magenta"))


def income_analysis():
    """Performs and displays income analysis for the current month vs. last month."""
    console = Console()
    transactions = _load_transactions()

    if not transactions:
        console.print("[bold yellow]No transactions found to analyze.[/bold yellow]")
        return

    now = datetime.now()
    current_month_start = now.replace(day=1)
    last_month_start = (current_month_start - relativedelta(months=1)).replace(day=1)

    current_month_income = [t for t in transactions if t['type'] == 'income' and t['date'] >= current_month_start]
    last_month_income = [t for t in transactions if t['type'] == 'income' and last_month_start <= t['date'] < current_month_start]

    total_current_month_income = sum(t['amount_paisa'] for t in current_month_income)
    total_last_month_income = sum(t['amount_paisa'] for t in last_month_income)
    
    console.print(Panel(f"[bold cyan]Income Analysis: {now.strftime('%B %Y')}[/bold cyan]", expand=False))

    # Income by source (current month)
    source_income = defaultdict(int)
    for income in current_month_income:
        source_income[income['category']] += income['amount_paisa']
    
    if total_current_month_income > 0:
        source_text = "\n".join([f"- {source}: {amount/100:.2f}" for source, amount in source_income.items()])
        console.print(Panel(source_text, title="Income by Source", border_style="green"))

        # Income stability
        stability = "Stable" if len(source_income) == 1 else "Varied"
        stability_text = f"You have {len(source_income)} source(s) of income this month. ({stability})"
        console.print(Panel(stability_text, title="Income Stability", border_style="yellow"))
    else:
        console.print("[yellow]No income recorded this month.[/yellow]")

    # Comparison
    trend = _get_trend_arrow(total_current_month_income, total_last_month_income)
    comparison_text = Text(f"Total This Month: {total_current_month_income/100:.2f}\n"
                           f"Total Last Month: {total_last_month_income/100:.2f}\n"
                           f"Trend: {trend}")
    console.print(Panel(comparison_text, title="Comparison", border_style="magenta"))


def savings_analysis():
    """Performs and displays savings analysis, including a 3-month trend."""
    console = Console()
    transactions = _load_transactions()
    if not transactions:
        console.print("[bold yellow]No transactions found to analyze.[/bold yellow]")
        return
        
    console.print(Panel("[bold cyan]Savings Analysis[/bold cyan]", expand=False))
    
    now = datetime.now()
    month_data = []

    for i in range(3): # Current month and previous two
        month_start = (now - relativedelta(months=i)).replace(day=1)
        next_month_start = (month_start + relativedelta(months=1))
        
        month_transactions = [t for t in transactions if month_start <= t['date'] < next_month_start]
        
        income = sum(t['amount_paisa'] for t in month_transactions if t['type'] == 'income')
        expense = sum(t['amount_paisa'] for t in month_transactions if t['type'] == 'expense')
        savings = income - expense
        savings_rate = (savings / income * 100) if income > 0 else 0
        
        month_data.append({
            "month": month_start.strftime("%B %Y"),
            "savings": savings,
            "savings_rate": savings_rate
        })
    
    month_data.reverse() # Show oldest first

    # Current month's detailed analysis
    current_month_stats = month_data[-1]
    current_savings_text = Text(f"This Month's Savings: {current_month_stats['savings']/100:.2f}\n"
                                f"This Month's Savings Rate: {current_month_stats['savings_rate']:.2f}%")
    console.print(Panel(current_savings_text, title=f"Statistics for {current_month_stats['month']}", border_style="green"))

    # 3-Month Trend
    trend_text = ""
    for i in range(len(month_data)):
        trend = ""
        if i > 0:
            trend = _get_trend_arrow(month_data[i]['savings'], month_data[i-1]['savings'])
        trend_text += f"{month_data[i]['month']}: {month_data[i]['savings']/100:.2f} ({month_data[i]['savings_rate']:.1f}%) {trend}\n"
    
    console.print(Panel(trend_text.strip(), title="Savings Trend (Last 3 Months)", border_style="yellow"))


def financial_health_score():
    """Calculates and displays a detailed financial health score."""
    console = Console()
    transactions = _load_transactions()
    budgets = _load_budgets()

    if not transactions:
        console.print("[bold yellow]No transactions found to calculate score.[/bold yellow]")
        return

    now = datetime.now()
    current_month_start = now.replace(day=1)
    
    current_month_trans = [t for t in transactions if t['date'] >= current_month_start]
    
    income = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'income')
    expenses = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'expense')
    
    # 1. Savings Rate (30 points)
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    savings_score = 0
    if savings_rate >= 20:
        savings_score = 30
    elif savings_rate >= 10:
        savings_score = 20
    elif savings_rate > 0:
        savings_score = 10

    # 2. Income vs Expenses (25 points)
    income_vs_expense_score = 25 if income > expenses else 5

    # 3. Budget Adherence (25 points)
    budget_adherence_score = 0
    if budgets:
        total_budgeted = sum(budgets.values())
        total_spent_in_budgeted_cats = 0
        for cat, budget_amt in budgets.items():
            spent = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'expense' and t['category'] == cat)
            total_spent_in_budgeted_cats += spent
        
        if total_budgeted > 0:
            over_budget_pct = (total_spent_in_budgeted_cats - total_budgeted) / total_budgeted
            if over_budget_pct <= 0:
                budget_adherence_score = 25      # Under budget
            elif over_budget_pct <= 0.1:
                budget_adherence_score = 15 # Slightly over
            else:
                budget_adherence_score = 5                          # Significantly over
    else: # No budgets set, give partial credit
        budget_adherence_score = 10 

    # 4. Debt Management (20 points) - Placeholder, as debt isn't tracked
    debt_score = 20 # Assume no debt for now

    total_score = savings_score + income_vs_expense_score + budget_adherence_score + debt_score
    
    # --- Display ---
    score_color = "green" if total_score >= 75 else "yellow" if total_score >= 50 else "red"
    console.print(Panel(f"[{score_color}]{total_score}/100[/]", title="Financial Health Score", border_style=score_color))

    # Breakdown
    breakdown_cols = [
        f"[b]Savings Rate:[/b]\n{savings_score}/30",
        f"[b]Budget Adherence:[/b]\n{budget_adherence_score}/25",
        f"[b]Income vs Expenses:[/b]\n{income_vs_expense_score}/25",
        f"[b]Debt Management:[/b]\n{debt_score}/20"
    ]
    console.print(Columns(breakdown_cols, equal=True, expand=True))

    # Recommendations
    recs = []
    if savings_score < 20:
        recs.append("• Aim to save at least 10-20% of your income.")
    if budget_adherence_score < 15:
        recs.append("• Create budgets for your spending categories and stick to them.")
    if income_vs_expense_score < 25:
        recs.append("• Your expenses are higher than your income. Review spending immediately.")
    
    if not recs:
        recs.append("• You're doing great! Keep up the good habits.")

    console.print(Panel("\n".join(recs), title="Recommendations", border_style="blue", padding=(1, 2)))


def generate_monthly_report():
    """Generates a comprehensive, well-styled monthly report."""
    console = Console()
    transactions = _load_transactions()
    budgets = _load_budgets()

    if not transactions:
        console.print("[bold yellow]No transactions found to generate report.[/bold yellow]")
        return
    
    now = datetime.now()
    month_name = now.strftime("%B %Y")
    
    console.print(Panel(f"[bold cyan]Monthly Financial Report: {month_name}[/bold cyan]", expand=False))

    # Data for current month
    current_month_start = now.replace(day=1)
    current_month_trans = [t for t in transactions if t['date'] >= current_month_start]
    
    income = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'income')
    expense = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'expense')
    savings = income - expense

    # 1. Overview
    overview_text = Text(f"Total Income: [green]{income/100:.2f}[/green]\n"
                         f"Total Expense: [red]{expense/100:.2f}[/red]\n"
                         f"Net Savings: [bold]{savings/100:.2f}[/bold]")
    console.print(Panel(overview_text, title="1. Month Overview", border_style="green"))

    # 2. Expense & Budget Performance
    expense_table = Table(title="Expense Breakdown", header_style="bold_magenta")
    expense_table.add_column("Category")
    expense_table.add_column("Spent", justify="right")
    expense_table.add_column("Budget", justify="right")
    expense_table.add_column("Variance", justify="right")

    category_spending = defaultdict(int)
    for exp in [t for t in current_month_trans if t['type'] == 'expense']:
        category_spending[exp['category']] += exp['amount_paisa']
    
    sorted_categories = sorted(category_spending.items(), key=lambda item: item[1], reverse=True)

    for category, spent_paisa in sorted_categories:
        budget_paisa = budgets.get(category, 0)
        variance_paisa = budget_paisa - spent_paisa
        color = "green" if variance_paisa >= 0 else "red"
        variance_text = f"[{color}]{variance_paisa/100:.2f}[/{color}]"
        expense_table.add_row(
            category, f"{spent_paisa/100:.2f}", 
            f"{budget_paisa/100:.2f}" if budget_paisa > 0 else "N/A", 
            variance_text
        )
    console.print(Panel(expense_table, title="2. Expense & Budget Performance", border_style="yellow"))

    # 3. Top Transactions
    top_trans = sorted([t for t in current_month_trans if t['type'] == 'expense'], key=lambda t: t['amount_paisa'], reverse=True)[:5]
    top_trans_text = ""
    if top_trans:
        top_trans_text = "\n".join([f"• {t['date'].strftime('%Y-%m-%d')}: {t['description']} ({t['category']}) - {t['amount_paisa']/100:.2f}" for t in top_trans])
    else:
        top_trans_text = "No expenses recorded this month."
    console.print(Panel(top_trans_text, title="3. Top 5 Largest Expenses", border_style="magenta"))
