"""
Transaction Manager
Handles CRUD operations for transactions
"""

import uuid
from datetime import datetime
from tabulate import tabulate


class TransactionManager:
    """Manages transaction operations using Spark backend"""

    # Predefined categories for expenses and income
    EXPENSE_CATEGORIES = [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Education",
        "Travel",
        "Groceries",
        "Other Expenses"
    ]

    INCOME_CATEGORIES = [
        "Salary",
        "Freelance",
        "Business",
        "Investment",
        "Gift",
        "Other Income"
    ]

    def __init__(self, spark_backend):
        """Initialize with Spark backend"""
        self.backend = spark_backend

    def add_transaction(self, transaction_type, category, amount, description="", date=None):
        """Add a new transaction"""
        if transaction_type not in ["income", "expense"]:
            print("Error: Transaction type must be 'income' or 'expense'")
            return False

        if amount <= 0:
            print("Error: Amount must be greater than 0")
            return False

        # Validate category
        valid_categories = self.INCOME_CATEGORIES if transaction_type == "income" else self.EXPENSE_CATEGORIES
        if category not in valid_categories:
            print(f"Warning: '{category}' is not a standard category.")

        # Use current date if not provided
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        transaction_data = {
            "transaction_id": str(uuid.uuid4()),
            "date": date,
            "type": transaction_type,
            "category": category,
            "amount": float(amount),
            "description": description,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        success = self.backend.add_transaction(transaction_data)
        if success:
            print(f"\n✓ Transaction added successfully!")
            print(f"  ID: {transaction_data['transaction_id']}")
            print(f"  Type: {transaction_type.capitalize()}")
            print(f"  Category: {category}")
            print(f"  Amount: ${amount:.2f}")
            print(f"  Date: {date}")
            return True
        else:
            print("✗ Failed to add transaction")
            return False

    def remove_transaction(self, transaction_id):
        """Remove a transaction by ID"""
        success = self.backend.remove_transaction(transaction_id)
        if success:
            print(f"\n✓ Transaction {transaction_id} removed successfully!")
            return True
        else:
            print(f"\n✗ Transaction {transaction_id} not found or could not be removed")
            return False

    def list_transactions(self, limit=None, transaction_type=None, category=None):
        """List all transactions with optional filters"""
        df = self.backend.get_all_transactions()

        if df is None or df.count() == 0:
            print("\nNo transactions found.")
            return

        # Apply filters
        if transaction_type:
            df = df.filter(df.type == transaction_type)

        if category:
            df = df.filter(df.category == category)

        # Convert to pandas for display
        transactions = df.orderBy("date", ascending=False).toPandas()

        if limit:
            transactions = transactions.head(limit)

        if len(transactions) == 0:
            print("\nNo transactions match the filters.")
            return

        # Format for display
        display_data = []
        for _, row in transactions.iterrows():
            display_data.append([
                row['transaction_id'][:8] + "...",
                row['date'],
                row['type'].capitalize(),
                row['category'],
                f"${row['amount']:.2f}",
                row['description'][:30] if row['description'] else ""
            ])

        headers = ["ID", "Date", "Type", "Category", "Amount", "Description"]
        print("\n" + tabulate(display_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal: {len(transactions)} transaction(s)")

    def get_categories(self, transaction_type=None):
        """Get available categories"""
        if transaction_type == "income":
            return self.INCOME_CATEGORIES
        elif transaction_type == "expense":
            return self.EXPENSE_CATEGORIES
        else:
            return {
                "income": self.INCOME_CATEGORIES,
                "expense": self.EXPENSE_CATEGORIES
            }

    def search_transactions(self, keyword):
        """Search transactions by description or category"""
        df = self.backend.get_all_transactions()

        if df is None or df.count() == 0:
            print("\nNo transactions found.")
            return

        # Filter by keyword in description or category
        filtered_df = df.filter(
            (df.description.contains(keyword)) |
            (df.category.contains(keyword))
        )

        if filtered_df.count() == 0:
            print(f"\nNo transactions found matching '{keyword}'")
            return

        # Convert to pandas for display
        transactions = filtered_df.orderBy("date", ascending=False).toPandas()

        display_data = []
        for _, row in transactions.iterrows():
            display_data.append([
                row['transaction_id'][:8] + "...",
                row['date'],
                row['type'].capitalize(),
                row['category'],
                f"${row['amount']:.2f}",
                row['description'][:30] if row['description'] else ""
            ])

        headers = ["ID", "Date", "Type", "Category", "Amount", "Description"]
        print("\n" + tabulate(display_data, headers=headers, tablefmt="grid"))
        print(f"\nFound: {len(transactions)} transaction(s)")

    def get_balance(self):
        """Calculate current balance (total income - total expenses)"""
        df = self.backend.get_all_transactions()

        if df is None or df.count() == 0:
            return 0.0

        from pyspark.sql import functions as F

        # Calculate total income
        income_df = df.filter(df.type == "income")
        total_income = income_df.agg(F.sum("amount")).collect()[0][0] or 0.0

        # Calculate total expenses
        expense_df = df.filter(df.type == "expense")
        total_expenses = expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0

        balance = total_income - total_expenses
        return balance
