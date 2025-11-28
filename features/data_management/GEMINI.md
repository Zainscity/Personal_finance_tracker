
## Goal
Enable users to manage their financial data effectively, including import/export and backup.

## Learning Focus
- File I/O operations (CSV, JSON)
- Data serialization/deserialization
- Error handling for file operations
- Data integrity and validation

## Fintech Concepts
- **Data Portability**: Ability to move data between systems
- **Backup & Restore**: Protecting data from loss
- **Data Privacy**: Ensuring sensitive financial data is handled securely

## Features to Build

### 1. Export Data

Allow users to export their transactions:
- Choose format: CSV or JSON.
- Specify date range (e.g., last month, last year, all time).
- Save to a user-specified file path.

### 2. Import Data

Allow users to import transactions:
- Support CSV or JSON format.
- Validate imported data (e.g., correct columns, valid dates, positive amounts).
- Handle duplicates (e.g., skip, overwrite, ask user). For simplicity, skip duplicates based on exact match of all fields.

### 3. Backup Data

Create a timestamped backup of `transactions.txt` and `budgets.txt` (future feature):
- Save to a `backups/` directory.
- Include current date and time in backup file names (e.g., `transactions_backup_2023-10-27_14-30-00.txt`).

### 4. Restore Data

Restore from a selected backup:
- List available backups.
- Allow user to choose a backup to restore.
- Warn user about overwriting current data.

## Success Criteria

✅ Can export transactions to CSV and JSON.
✅ Can import transactions from CSV and JSON with validation.
✅ Can create timestamped backups of data files.
✅ Can restore data from a selected backup.
✅ Handles file I/O errors gracefully.
