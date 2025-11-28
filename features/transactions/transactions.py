import questionary
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from features.budgets.budgets import check_budget_alert
from utils.constants import EXPENSE_CATEGORIES, INCOME_CATEGORIES # New import

# File path for transactions
TRANSACTIONS_FILE = "database/transactions.txt"

def add_expense():
    """Adds an expense transaction."""
    console = Console()
    try:
        amount_str = questionary.text(
            "Enter the expense amount:",
            validate=lambda text: text.isdigit() and float(text) > 0,
            qmark="💸"
        ).ask()
        if not amount_str:
            console.print("[bold red]Expense amount cannot be empty.[/bold red]")
            return

        amount_paisa = int(float(amount_str) * 100)

        category = questionary.select(
            "Select expense category:",
            choices=EXPENSE_CATEGORIES,
            qmark="🏷️"
        ).ask()
        if not category:
            console.print("[bold red]Category selection cancelled.[/bold red]")
            return

        description = questionary.text("Enter a description:", qmark="📝").ask()
        if not description:
            description = "" # Allow empty description

        date_str = questionary.text(
            "Enter the date (YYYY-MM-DD):",
            default=datetime.now().strftime("%Y-%m-%d"),
            qmark="📅"
        ).ask()
        if not date_str:
            console.print("[bold red]Date cannot be empty.[/bold red]")
            return

        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            console.print("[bold red]Invalid date format. Please use YYYY-MM-DD.[/bold red]")
            return

        # Check for budget alert before saving
        check_budget_alert(category, amount_paisa)

        with open(TRANSACTIONS_FILE, "a") as f:
            f.write(f"{date_str},expense,{category},{amount_paisa},{description}\n")

        console.print(f"[bold green]✅ Expense of {float(amount_paisa)/100:.2f} in '{category}' added successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Transaction cancelled.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def add_income():
    """Adds an income transaction."""
    console = Console()
    try:
        amount_str = questionary.text(
            "Enter the income amount:",
            validate=lambda text: text.isdigit() and float(text) > 0,
            qmark="💰"
        ).ask()
        if not amount_str:
            console.print("[bold red]Income amount cannot be empty.[/bold red]")
            return

        amount_paisa = int(float(amount_str) * 100)

        category = questionary.select(
            "Select income source:",
            choices=INCOME_CATEGORIES,
            qmark="S"
        ).ask()
        if not category:
            console.print("[bold red]Source selection cancelled.[/bold red]")
            return

        description = questionary.text("Enter a description:", qmark="📝").ask()
        if not description:
            description = "" # Allow empty description

        date_str = questionary.text(
            "Enter the date (YYYY-MM-DD):",
            default=datetime.now().strftime("%Y-%m-%d"),
            qmark="📅"
        ).ask()
        if not date_str:
            console.print("[bold red]Date cannot be empty.[/bold red]")
            return

        # Validate date format
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            console.print("[bold red]Invalid date format. Please use YYYY-MM-DD.[/bold red]")
            return

        with open(TRANSACTIONS_FILE, "a") as f:
            f.write(f"{date_str},income,{category},{amount_paisa},{description}\n")

        console.print(f"[bold green]✅ Income of {float(amount_paisa)/100:.2f} from '{category}' added successfully![/bold green]")

    except KeyboardInterrupt:
        console.print("\n[bold yellow]Transaction cancelled.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def list_transactions():
    """Lists all transactions based on a user-selected filter."""
    console = Console()
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            lines = f.readlines()

        if not lines:
            console.print("[bold yellow]No transactions found.[/bold yellow]")
            return

        # Ask user for filter
        filter_choice = questionary.select(
            "Filter transactions by:",
            choices=["All Transactions", "Last 7 Days", "Expenses Only", "Income Only", "Cancel"],
            qmark="🔍"
        ).ask()

        if not filter_choice or filter_choice == "Cancel":
            console.print("[bold yellow]Operation cancelled.[/bold yellow]")
            return
            
        transactions = []
        for line in lines:
            date_str, type, category, amount_paisa, description = line.strip().split(',', 4)
            transactions.append({
                "date": datetime.strptime(date_str, "%Y-%m-%d"),
                "type": type,
                "category": category,
                "amount_paisa": int(amount_paisa),
                "description": description
            })

        # Apply filter
        filtered_transactions = []
        if filter_choice == "All Transactions":
            filtered_transactions = transactions
        elif filter_choice == "Last 7 Days":
            seven_days_ago = datetime.now() - timedelta(days=7)
            filtered_transactions = [t for t in transactions if t['date'] >= seven_days_ago]
        elif filter_choice == "Expenses Only":
            filtered_transactions = [t for t in transactions if t['type'] == 'expense']
        elif filter_choice == "Income Only":
            filtered_transactions = [t for t in transactions if t['type'] == 'income']

        if not filtered_transactions:
            console.print("[bold yellow]No transactions found for the selected filter.[/bold yellow]")
            return
            
        table = Table(title=f"Transactions ({filter_choice})", show_header=True, header_style="bold magenta")
        table.add_column("Date", style="dim", width=12)
        table.add_column("Type", width=8)
        table.add_column("Category", width=15)
        table.add_column("Description")
        table.add_column("Amount", justify="right")

        # Sort by date (newest first)
        filtered_transactions.sort(key=lambda t: t['date'], reverse=True)

        for t in filtered_transactions:
            amount = t['amount_paisa'] / 100
            color = "red" if t['type'] == "expense" else "green"
            table.add_row(
                t['date'].strftime("%Y-%m-%d"),
                f"[{color}]{t['type'].capitalize()}[/{color}]",
                t['category'],
                t['description'],
                f"[{color}]{amount:.2f}[/{color}]"
            )

        console.print(table)

    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def show_balance():
    """Shows the current balance for the current month."""
    console = Console()
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            lines = f.readlines()

        if not lines:
            console.print("[bold yellow]No transactions found.[/bold yellow]")
            return

        total_income = 0
        total_expense = 0
        current_month = datetime.now().strftime("%Y-%m")

        for line in lines:
            date_str, type, _, amount_paisa, _ = line.strip().split(',', 4)
            if date_str.startswith(current_month):
                amount = int(amount_paisa)
                if type == "income":
                    total_income += amount
                else:
                    total_expense += amount

        balance = total_income - total_expense

        console.print(f"Balance for {datetime.now().strftime('%B %Y')}:")
        console.print(f"[green]Total Income: {total_income/100:.2f}[/green]")
        console.print(f"[red]Total Expense: {total_expense/100:.2f}[/red]")

        balance_color = "green" if balance >= 0 else "red"
        console.print(f"Current Balance: [{balance_color}]{balance/100:.2f}[/{balance_color}]")

    except FileNotFoundError:
        console.print("[bold yellow]No transactions found.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
