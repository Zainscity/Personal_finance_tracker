import questionary
from rich.console import Console
from collections import defaultdict
from datetime import datetime
from rich.table import Table
from utils.constants import EXPENSE_CATEGORIES # New import

# File paths
BUDGETS_FILE = "database/budgets.txt"
TRANSACTIONS_FILE = "database/transactions.txt" # Needed for viewing budgets

def set_budget():
    """Allows users to set a monthly budget for an expense category."""
    console = Console()
    console.print("[bold blue]Setting Budget...[/bold blue]")

    category = questionary.select(
        "Select expense category to set budget for:",
        choices=EXPENSE_CATEGORIES,
        qmark="🏷️"
    ).ask()
    if not category:
        console.print("[bold red]Category selection cancelled.[/bold red]")
        return

    amount_str = questionary.text(
        f"Enter monthly budget amount for {category}:",
        validate=lambda text: text.isdigit() and float(text) > 0,
        qmark="💰"
    ).ask()
    if not amount_str:
        console.print("[bold red]Budget amount cannot be empty.[/bold red]")
        return

    budget_amount_paisa = int(float(amount_str) * 100)

    # Read existing budgets
    budgets = {}
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    cat, amount = parts
                    budgets[cat] = int(amount)
    except FileNotFoundError:
        pass # File will be created if it doesn't exist

    budgets[category] = budget_amount_paisa

    # Write updated budgets
    try:
        with open(BUDGETS_FILE, "w") as f:
            for cat, amount in budgets.items():
                f.write(f"{cat},{amount}\n")
        console.print(f"[bold green]✅ Monthly budget of {budget_amount_paisa/100:.2f} set for '{category}' successfully![/bold green]")
    except IOError as e:
        console.print(f"[bold red]Error saving budget: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

def view_budgets():
    """Displays all set budgets with actual spending and remaining/overrun."""
    console = Console()
    console.print("[bold blue]Viewing Budgets...[/bold blue]")

    budgets = {}
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    cat, amount = parts
                    budgets[cat] = int(amount)
    except FileNotFoundError:
        console.print("[bold yellow]No budgets set yet.[/bold yellow]")
        return

    if not budgets:
        console.print("[bold yellow]No budgets set yet.[/bold yellow]")
        return

    # Read transactions to calculate actual spending
    transactions = []
    try:
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
    except FileNotFoundError:
        pass # No transactions yet, actual spending will be 0

    actual_spending = defaultdict(int)
    current_month = datetime.now().strftime("%Y-%m")

    for t in transactions:
        if t['type'] == 'expense' and t['date'].strftime("%Y-%m") == current_month:
            actual_spending[t['category']] += t['amount_paisa']

    table = Table(title="Monthly Budgets", show_header=True, header_style="bold magenta")
    table.add_column("Category", style="dim", width=15)
    table.add_column("Budget", justify="right")
    table.add_column("Spent", justify="right")
    table.add_column("Remaining/Overrun", justify="right")

    for category, budgeted_amount_paisa in budgets.items():
        spent_amount_paisa = actual_spending[category]
        remaining_paisa = budgeted_amount_paisa - spent_amount_paisa

        remaining_color = "green" if remaining_paisa >= 0 else "red"

        table.add_row(
            category,
            f"{budgeted_amount_paisa/100:.2f}",
            f"{spent_amount_paisa/100:.2f}",
            f"[{remaining_color}]{remaining_paisa/100:.2f}[/{remaining_color}]"
        )
    console.print(table)

def check_budget_alert(category, expense_amount_paisa):
    """Checks if an expense causes a budget overrun and displays a warning."""
    console = Console()

    budgets = {}
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    cat, amount = parts
                    budgets[cat] = int(amount)
    except FileNotFoundError:
        return # No budgets set, so no alerts

    budgeted_amount_paisa = budgets.get(category)
    if budgeted_amount_paisa is None:
        return # No budget for this category

    # Calculate current spending for the category this month
    current_spending_paisa = 0
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(',', 4)
                if len(parts) == 5:
                    date_str, type, trans_category, amount_paisa_str, _ = parts
                    if type == 'expense' and trans_category == category and \
                       datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m") == datetime.now().strftime("%Y-%m"):
                        current_spending_paisa += int(amount_paisa_str)
    except FileNotFoundError:
        pass # No transactions yet

    projected_spending_paisa = current_spending_paisa + expense_amount_paisa

    if projected_spending_paisa > budgeted_amount_paisa:
        overrun_amount_paisa = projected_spending_paisa - budgeted_amount_paisa
        console.print(f"[bold red]🚨 Budget Alert! Your spending in '{category}' will exceed its monthly budget by {overrun_amount_paisa/100:.2f}![/bold red]")
    elif projected_spending_paisa > budgeted_amount_paisa * 0.9: # Warn at 90%
        remaining_paisa = budgeted_amount_paisa - projected_spending_paisa
        console.print(f"[bold yellow]⚠️ Warning! You are close to exceeding your budget for '{category}'. {remaining_paisa/100:.2f} remaining.[/bold yellow]")
