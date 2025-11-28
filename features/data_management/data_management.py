import questionary
from datetime import datetime, timedelta
from rich.console import Console
import csv
import json
import os
import shutil

# File paths
TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt" # Future use
BACKUPS_DIR = "backups"

def export_data():
    """Exports transactions to CSV or JSON, with date filtering."""
    console = Console()
    console.print("[bold blue]Exporting Data...[/bold blue]")

    # Read transactions
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            transactions = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        console.print("[bold yellow]No transactions found to export.[/bold yellow]")
        return

    if not transactions:
        console.print("[bold yellow]No transactions found to export.[/bold yellow]")
        return

    # Ask for format
    export_format = questionary.select(
        "Select export format:", choices=["CSV", "JSON", "Cancel"], qmark="📄"
    ).ask()
    if not export_format or export_format == "Cancel":
        console.print("[bold red]Export cancelled.[/bold red]")
        return

    # Ask for date range
    date_range_choice = questionary.select(
        "Select date range:",
        choices=["All time", "This month", "Last month", "This year", "Custom"],
        qmark="📅"
    ).ask()
    if not date_range_choice:
        console.print("[bold red]Export cancelled.[/bold red]")
        return

    # Filter transactions
    now = datetime.now()
    filtered_transactions = []
    
    start_date, end_date = None, None
    if date_range_choice == "This month":
        start_date = now.replace(day=1)
    elif date_range_choice == "Last month":
        end_date = now.replace(day=1) - timedelta(days=1)
        start_date = end_date.replace(day=1)
    elif date_range_choice == "This year":
        start_date = now.replace(month=1, day=1)
    elif date_range_choice == "Custom":
        start_str = questionary.text("Enter start date (YYYY-MM-DD):").ask()
        end_str = questionary.text("Enter end date (YYYY-MM-DD):").ask()
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            console.print("[bold red]Invalid date format. Export cancelled.[/bold red]")
            return
            
    for line in transactions:
        date_str = line.split(',')[0]
        t_date = datetime.strptime(date_str, "%Y-%m-%d")
        if (start_date and t_date < start_date) or (end_date and t_date > end_date):
            continue
        filtered_transactions.append(line)

    if not filtered_transactions:
        console.print("[bold yellow]No transactions found in the selected date range.[/bold yellow]")
        return

    # Prepare data for export
    export_data = []
    for line in filtered_transactions:
        date_str, type, category, amount_paisa, description = line.split(',', 4)
        export_data.append({
            "date": date_str, "type": type, "category": category, 
            "amount_paisa": int(amount_paisa), "description": description
        })

    # Ask for file path and save
    output_file = questionary.text(f"Enter output file path (e.g., 'export.{export_format.lower()}'):").ask()
    if not output_file:
        console.print("[bold red]Export cancelled.[/bold red]")
        return

    try:
        if export_format == "CSV":
            with open(output_file, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
        elif export_format == "JSON":
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=4)
        console.print(f"[bold green]✅ {len(export_data)} transactions exported successfully to {output_file}![/bold green]")
    except (IOError, Exception) as e:
        console.print(f"[bold red]Error exporting data: {e}[/bold red]")


def import_data():
    """Imports transactions from a CSV or JSON file, skipping duplicates."""
    console = Console()
    console.print("[bold blue]Importing Data...[/bold blue]")
    
    file_path = questionary.text("Enter the path of the file to import:").ask()
    if not file_path or not os.path.exists(file_path):
        console.print("[bold red]File not found or import cancelled.[/bold red]")
        return

    # Load existing transactions to prevent duplicates
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            existing_lines = {line.strip() for line in f.readlines()}
    except FileNotFoundError:
        existing_lines = set()

    # Read and validate new transactions
    new_transactions = []
    try:
        if file_path.lower().endswith('.csv'):
            with open(file_path, "r", newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    new_transactions.append(row)
        elif file_path.lower().endswith('.json'):
            with open(file_path, "r") as f:
                new_transactions = json.load(f)
        else:
            console.print("[bold red]Unsupported file format. Please use CSV or JSON.[/bold red]")
            return
    except (IOError, json.JSONDecodeError, csv.Error) as e:
        console.print(f"[bold red]Error reading or parsing the file: {e}[/bold red]")
        return

    added_count = 0
    skipped_count = 0
    
    with open(TRANSACTIONS_FILE, "a") as f:
        for t in new_transactions:
            try:
                # Basic validation
                date_str = t['date']
                datetime.strptime(date_str, "%Y-%m-%d") # Validate date
                amount = int(t['amount_paisa'])
                if amount <= 0:
                    raise ValueError("Amount must be positive.")
                
                line_to_add = f"{date_str},{t['type']},{t['category']},{amount},{t['description']}"

                if line_to_add in existing_lines:
                    skipped_count += 1
                else:
                    f.write(line_to_add + "\n")
                    existing_lines.add(line_to_add)
                    added_count += 1
            except (KeyError, ValueError) as e:
                console.print(f"[bold yellow]Skipping invalid record: {t}. Reason: {e}[/bold yellow]")
                skipped_count += 1

    console.print("[bold green]✅ Import complete![/bold green]")
    console.print(f"  - {added_count} new transactions added.")
    console.print(f"  - {skipped_count} duplicate or invalid records skipped.")

def backup_data():
    """Creates a timestamped backup of the entire database directory."""
    console = Console()
    console.print("[bold blue]Backing up Data...[/bold blue]")
    
    if not os.path.exists(TRANSACTIONS_FILE) and not os.path.exists(BUDGETS_FILE):
        console.print("[bold yellow]No data files found to back up.[/bold yellow]")
        return

    try:
        os.makedirs(BACKUPS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = os.path.join(BACKUPS_DIR, f"backup-{timestamp}")
        
        # Create a zip archive of the database directory
        shutil.make_archive(backup_filename, 'zip', 'database')
        
        console.print(f"[bold green]✅ Backup created successfully at {backup_filename}.zip[/bold green]")

    except Exception as e:
        console.print(f"[bold red]An error occurred during backup: {e}[/bold red]")

def restore_data():
    """Restores data from a selected backup."""
    console = Console()
    console.print("[bold blue]Restoring Data...[/bold blue]")
    
    if not os.path.exists(BACKUPS_DIR):
        console.print("[bold yellow]No backup directory found.[/bold yellow]")
        return

    backups = [f for f in os.listdir(BACKUPS_DIR) if f.endswith('.zip')]
    if not backups:
        console.print("[bold yellow]No backups found.[/bold yellow]")
        return
        
    # Sort by date, newest first
    backups.sort(reverse=True)

    backup_choice = questionary.select(
        "Select a backup to restore:",
        choices=backups + ["Cancel"],
        qmark="🗳️"
    ).ask()

    if not backup_choice or backup_choice == "Cancel":
        console.print("[bold red]Restore cancelled.[/bold red]")
        return

    confirm = questionary.confirm(
        "⚠️ This will overwrite all current data. Are you sure you want to proceed?",
        default=False
    ).ask()

    if not confirm:
        console.print("[bold red]Restore cancelled.[/bold red]")
        return

    try:
        backup_path = os.path.join(BACKUPS_DIR, backup_choice)
        
        # Extract the zip file to the root directory, which will overwrite files in 'database/'
        shutil.unpack_archive(backup_path, '.', 'zip')
        
        console.print(f"[bold green]✅ Data restored successfully from {backup_choice}[/bold green]")
        console.print("[bold yellow]It's recommended to restart the application.[/bold yellow]")

    except Exception as e:
        console.print(f"[bold red]An error occurred during restore: {e}[/bold red]")