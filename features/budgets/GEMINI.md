## Goal
Enable users to set and track budgets for different spending categories.

## Learning Focus
- Data storage and retrieval for budgets
- Budget calculation and comparison with actual spending
- Alert generation for budget overruns

## Fintech Concepts
- **Budgeting**: Allocating funds for specific purposes
- **Budget Variance**: Difference between budgeted and actual amounts
- **Budget Alerts**: Notifications when approaching or exceeding budget limits

## Features to Build

### 1. Set Budget

Allow users to set a monthly budget for each expense category:
- Ask for category (from existing expense categories).
- Ask for monthly budget amount (validate: positive number).
- Save to `budgets.txt`. Overwrite if budget for category already exists.

### 2. View Budgets

Display all set budgets:
- Show category and budgeted amount.
- Show actual spending for the current month in that category.
- Show remaining budget or overrun.
- Use Rich table for display.

### 3. Budget Alerts (Basic)

When adding an expense:
- Check if the expense causes an overrun in the category's budget.
- If so, display a warning message.

## Success Criteria

✅ Can set monthly budgets for expense categories.
✅ Can view all set budgets with actual spending and remaining/overrun amounts.
✅ Receives a warning when an expense exceeds a category's budget.
✅ Budget data is stored persistently.
