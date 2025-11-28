from datetime import datetime
from dateutil.relativedelta import relativedelta
from rich.console import Console
from rich.panel import Panel
from collections import defaultdict
import os

# Assuming analytics helpers can be imported or recreated here for score calculation
# To avoid circular dependency, we might need a shared helper module, but for now, let's redefine
def _load_transactions_for_assistant():
    if not os.path.exists("database/transactions.txt"):
        return []
    transactions = []
    with open("database/transactions.txt", "r") as f:
        for line in f:
            parts = line.strip().split(',', 4)
            if len(parts) == 5:
                date_str, type, category, amount_paisa, description = parts
                transactions.append({
                    "date": datetime.strptime(date_str, "%Y-%m-%d"),
                    "type": type, "category": category, 
                    "amount_paisa": int(amount_paisa), "description": description
                })
    return transactions

def _load_budgets_for_assistant():
    if not os.path.exists("database/budgets.txt"):
        return {}
    budgets = {}
    with open("database/budgets.txt", "r") as f:
        for line in f:
            parts = line.strip().split(',', 1)
            if len(parts) == 2:
                budgets[parts[0]] = int(parts[1])
    return budgets

# A simplified, self-contained health score calculation for the assistant
def _calculate_health_score(transactions, budgets):
    now = datetime.now()
    current_month_start = now.replace(day=1)
    current_month_trans = [t for t in transactions if t['date'] >= current_month_start]
    
    income = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'income')
    expenses = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'expense')
    
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    savings_score = min(30, max(0, (savings_rate / 20) * 30))

    income_vs_expense_score = 25 if income > expenses else 5
    
    budget_adherence_score = 10 # Default partial credit
    if budgets:
        total_budgeted = sum(budgets.values())
        spent_in_budgeted_cats = sum(t['amount_paisa'] for t in current_month_trans if t['type'] == 'expense' and t['category'] in budgets)
        if total_budgeted > 0 and spent_in_budgeted_cats <= total_budgeted:
            budget_adherence_score = 25
        elif total_budgeted > 0 and spent_in_budgeted_cats > total_budgeted:
            budget_adherence_score = 5

    debt_score = 20 # Placeholder
    return savings_score + income_vs_expense_score + budget_adherence_score + debt_score

def generate_recommendations():
    """Generates and displays intelligent financial recommendations."""
    console = Console()
    console.print(Panel("[bold cyan]Smart Financial Assistant[/bold cyan]", expand=False))

    transactions = _load_transactions_for_assistant()
    budgets = _load_budgets_for_assistant()

    if not transactions:
        console.print("[bold yellow]No transactions found. Start by adding some income and expenses![/bold yellow]")
        return

    now = datetime.now()
    current_month_start = now.replace(day=1)
    current_month_expenses = [t for t in transactions if t['type'] == 'expense' and t['date'] >= current_month_start]
    current_month_income = sum(t['amount_paisa'] for t in transactions if t['type'] == 'income' and t['date'] >= current_month_start)

    # --- 1. Spending Recommendations ---
    rec_panel_1_content = ""
    if current_month_expenses:
        category_spending = defaultdict(int)
        for expense in current_month_expenses:
            category_spending[expense['category']] += expense['amount_paisa']
        
        sorted_categories = sorted(category_spending.items(), key=lambda item: item[1], reverse=True)
        top_category, top_amount = sorted_categories[0]
        
        rec_panel_1_content += f"• Your top spending category this month is [bold red]{top_category}[/bold red] at {top_amount/100:.2f}.\n"
        if top_category == 'Food':
            rec_panel_1_content += "  ↳ Consider packing lunch or looking for deals to reduce food costs.\n"
        elif top_category == 'Shopping':
            rec_panel_1_content += "  ↳ Try a 'no-spend' week or unsubscribe from marketing emails.\n"
        elif top_category == 'Transport':
            rec_panel_1_content += "  ↳ Could you use public transport or carpool more often?\n"

        total_current_month_expense = sum(t['amount_paisa'] for t in current_month_expenses)
        for expense in current_month_expenses:
            if expense['amount_paisa'] > 0.25 * total_current_month_expense: # Alert if > 25%
                rec_panel_1_content += f"• [yellow]Alert:[/yellow] A large expense of {expense['amount_paisa']/100:.2f} for '{expense['description']}' seems high.\n"
    else:
        rec_panel_1_content = "• No expenses this month to analyze."
    console.print(Panel(rec_panel_1_content.strip(), title="[bold green]Spending Insights[/bold green]", border_style="green"))

    # --- 2. Savings Recommendations ---
    rec_panel_2_content = ""
    three_months_ago = now - relativedelta(months=3)
    recent_income = sum(t['amount_paisa'] for t in transactions if t['type'] == 'income' and t['date'] >= three_months_ago)
    avg_monthly_income = recent_income / 3 if recent_income > 0 else 0

    if avg_monthly_income > 0:
        target_savings = avg_monthly_income * 0.15 # Suggest saving 15%
        rec_panel_2_content += f"• Based on your average income, a good monthly savings goal is around [bold green]{target_savings/100:.2f}[/bold green] (15%).\n"
        
        current_savings = current_month_income - sum(e['amount_paisa'] for e in current_month_expenses)
        if current_savings < target_savings:
            rec_panel_2_content += f"  ↳ You've saved {current_savings/100:.2f} so far. You are behind your target!\n"
        else:
            rec_panel_2_content += f"  ↳ You've saved {current_savings/100:.2f} this month. Great job, you're on track!\n"
    else:
        rec_panel_2_content = "• Not enough income data to suggest a savings target."
    console.print(Panel(rec_panel_2_content.strip(), title="[bold yellow]Savings Goals[/bold yellow]", border_style="yellow"))

    # --- 3. Budget Adherence Tips ---
    rec_panel_3_content = ""
    if budgets:
        for category, budget_amount in budgets.items():
            spent = sum(e['amount_paisa'] for e in current_month_expenses if e['category'] == category)
            if spent > budget_amount:
                overspend = (spent - budget_amount) / 100
                rec_panel_3_content += f"• [red]Over budget![/red] You've spent {overspend:.2f} too much in '{category}'.\n"
            elif spent > budget_amount * 0.8:
                remaining = (budget_amount - spent) / 100
                rec_panel_3_content += f"• [yellow]Nearing limit![/yellow] Only {remaining:.2f} left in your '{category}' budget.\n"
        if not rec_panel_3_content:
            rec_panel_3_content = "• You are staying within all your budget limits. Keep it up!"
    else:
        rec_panel_3_content = "• You don't have any budgets set. Consider setting budgets to control your spending."
    console.print(Panel(rec_panel_3_content.strip(), title="[bold magenta]Budget Tips[/bold magenta]", border_style="magenta"))
    
    # --- 4. Financial Health Tips ---
    rec_panel_4_content = ""
    health_score = _calculate_health_score(transactions, budgets)
    
    rec_panel_4_content += f"• Your current financial health score is [bold]{health_score:.0f}/100[/bold].\n"
    if health_score < 50:
        rec_panel_4_content += "  ↳ Focus on the basics: Track all spending and create a budget for key categories."
    elif health_score < 75:
        rec_panel_4_content += "  ↳ You're on the right track. Look for ways to increase your savings rate."
    else:
        rec_panel_4_content += "  ↳ Excellent! Consider setting long-term financial goals."
    console.print(Panel(rec_panel_4_content.strip(), title="[bold blue]Financial Health[/bold blue]", border_style="blue"))