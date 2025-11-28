import questionary
from rich.console import Console

from features.transactions.transactions import add_expense, add_income, list_transactions, show_balance
from features.analytics.analytics import spending_analysis, income_analysis, savings_analysis, financial_health_score, generate_monthly_report
from features.smart_assistant.smart_assistant import generate_recommendations
from features.data_management.data_management import export_data, import_data, backup_data, restore_data
from features.budgets.budgets import set_budget, view_budgets # New import

def analytics_menu():
    """Displays the analytics menu and handles user choices."""
    while True:
        choice = questionary.select(
            "Financial Analytics Menu:",
            choices=[
                "Spending Analysis",
                "Income Analysis",
                "Savings Analysis",
                "Financial Health Score",
                "Generate Monthly Report",
                "Back to Main Menu",
            ],
            qmark="📊"
        ).ask()

        if choice == "Spending Analysis":
            spending_analysis()
        elif choice == "Income Analysis":
            income_analysis()
        elif choice == "Savings Analysis":
            savings_analysis()
        elif choice == "Financial Health Score":
            financial_health_score()
        elif choice == "Generate Monthly Report":
            generate_monthly_report()
        elif choice == "Back to Main Menu" or choice is None:
            break

def data_management_menu():
    """Displays the data management menu and handles user choices."""
    while True:
        choice = questionary.select(
            "Data Management Menu:",
            choices=[
                "Export Data",
                "Import Data",
                "Backup Data",
                "Restore Data",
                "Back to Main Menu",
            ],
            qmark="🗄️"
        ).ask()

        if choice == "Export Data":
            export_data()
        elif choice == "Import Data":
            import_data()
        elif choice == "Backup Data":
            backup_data()
        elif choice == "Restore Data":
            restore_data()
        elif choice == "Back to Main Menu" or choice is None:
            break

def budget_management_menu(): # New menu function
    """Displays the budget management menu and handles user choices."""
    while True:
        choice = questionary.select(
            "Budget Management Menu:",
            choices=[
                "Set Budget",
                "View Budgets",
                "Back to Main Menu",
            ],
            qmark="💰"
        ).ask()

        if choice == "Set Budget":
            set_budget()
        elif choice == "View Budgets":
            view_budgets()
        elif choice == "Back to Main Menu" or choice is None:
            break

def main():
    """Main function to run the CLI application."""
    console = Console()
    console.print("[bold cyan]Welcome to your Personal Finance Tracker![/bold cyan]")

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "Add Expense",
                "Add Income",
                "List Transactions",
                "Show Balance",
                "Financial Analytics",
                "Smart Assistant",
                "Data Management",
                "Budget Management", # New option
                "Exit",
            ],
            qmark=">"
        ).ask()

        if choice == "Add Expense":
            add_expense()
        elif choice == "Add Income":
            add_income()
        elif choice == "List Transactions":
            list_transactions()
        elif choice == "Show Balance":
            show_balance()
        elif choice == "Financial Analytics":
            analytics_menu()
        elif choice == "Smart Assistant":
            generate_recommendations()
        elif choice == "Data Management":
            data_management_menu()
        elif choice == "Budget Management": # Call budget management menu
            budget_management_menu()
        elif choice == "Exit" or choice is None:
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break

if __name__ == "__main__":
    main()