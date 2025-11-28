#!/usr/bin/env python3
"""
Sample Usage Script
Demonstrates how to use the Personal Finance Tracker programmatically
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spark_backend import SparkBackend
from transaction_manager import TransactionManager
from report_generator import ReportGenerator
from csv_exporter import CSVExporter
from visualizer import DataVisualizer


def create_sample_data():
    """Create sample transactions for demonstration"""
    print("Creating sample data...")

    # Initialize backend
    backend = SparkBackend(data_path="data/transactions")
    backend.load_data()

    tm = TransactionManager(backend)

    # Sample income transactions
    sample_income = [
        ("income", "Salary", 5000, "Monthly salary", "2025-01-15"),
        ("income", "Freelance", 1500, "Website development project", "2025-01-20"),
        ("income", "Salary", 5000, "Monthly salary", "2025-02-15"),
        ("income", "Investment", 200, "Stock dividends", "2025-02-25"),
        ("income", "Salary", 5000, "Monthly salary", "2025-03-15"),
    ]

    # Sample expense transactions
    sample_expenses = [
        ("expense", "Food & Dining", 450, "Groceries and restaurants", "2025-01-05"),
        ("expense", "Transportation", 150, "Gas and public transport", "2025-01-08"),
        ("expense", "Bills & Utilities", 300, "Electric and internet", "2025-01-10"),
        ("expense", "Shopping", 200, "New clothes", "2025-01-12"),
        ("expense", "Entertainment", 100, "Movie tickets and streaming", "2025-01-18"),
        ("expense", "Healthcare", 80, "Pharmacy", "2025-01-22"),
        ("expense", "Food & Dining", 480, "Groceries and restaurants", "2025-02-05"),
        ("expense", "Transportation", 160, "Gas and public transport", "2025-02-08"),
        ("expense", "Bills & Utilities", 310, "Electric and internet", "2025-02-10"),
        ("expense", "Entertainment", 120, "Concert tickets", "2025-02-14"),
        ("expense", "Education", 500, "Online course", "2025-02-20"),
        ("expense", "Food & Dining", 500, "Groceries and restaurants", "2025-03-05"),
        ("expense", "Transportation", 140, "Gas and public transport", "2025-03-08"),
        ("expense", "Bills & Utilities", 290, "Electric and internet", "2025-03-10"),
        ("expense", "Travel", 800, "Weekend trip", "2025-03-15"),
        ("expense", "Shopping", 250, "Electronics", "2025-03-18"),
    ]

    # Add all transactions
    print("\nAdding income transactions...")
    for trans in sample_income:
        tm.add_transaction(*trans)

    print("\nAdding expense transactions...")
    for trans in sample_expenses:
        tm.add_transaction(*trans)

    # Save data
    backend.save_data()
    print("\n✓ Sample data created successfully!")

    return backend, tm


def demonstrate_features():
    """Demonstrate all features of the application"""
    print("\n" + "=" * 70)
    print("PERSONAL FINANCE TRACKER - FEATURE DEMONSTRATION")
    print("=" * 70)

    # Initialize components
    backend = SparkBackend(data_path="data/transactions")
    backend.load_data()

    tm = TransactionManager(backend)
    rg = ReportGenerator(backend)
    ce = CSVExporter(backend)
    viz = DataVisualizer(backend)

    # 1. List recent transactions
    print("\n[1] RECENT TRANSACTIONS")
    print("-" * 70)
    tm.list_transactions(limit=10)

    # 2. View balance
    print("\n[2] CURRENT BALANCE")
    print("-" * 70)
    balance = tm.get_balance()
    print(f"Current Balance: ${balance:,.2f}")

    # 3. Monthly report
    print("\n[3] MONTHLY REPORT - MARCH 2025")
    print("-" * 70)
    rg.monthly_summary(2025, 3)

    # 4. Yearly report
    print("\n[4] YEARLY REPORT - 2025")
    print("-" * 70)
    rg.yearly_summary(2025)

    # 5. Category report
    print("\n[5] CATEGORY REPORT - FOOD & DINING")
    print("-" * 70)
    rg.category_report("Food & Dining")

    # 6. Export to CSV
    print("\n[6] EXPORTING DATA TO CSV")
    print("-" * 70)
    ce.export_all_transactions()
    ce.export_by_type("expense")
    ce.export_monthly_summary(2025, 3)

    # 7. Create visualizations
    print("\n[7] CREATING VISUALIZATIONS")
    print("-" * 70)
    viz.plot_expense_by_category()
    viz.plot_income_vs_expenses()
    viz.plot_monthly_trend(2025)
    viz.plot_category_comparison()

    # Cleanup
    backend.stop()

    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE!")
    print("=" * 70)
    print("\nCheck the following directories:")
    print("  - exports/         : CSV files")
    print("  - visualizations/  : PNG charts")
    print("  - data/transactions: Parquet data files")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Personal Finance Tracker - Sample Usage")
    parser.add_argument("--create-sample", action="store_true",
                        help="Create sample transaction data")
    parser.add_argument("--demo", action="store_true",
                        help="Run feature demonstration")

    args = parser.parse_args()

    if args.create_sample:
        create_sample_data()
    elif args.demo:
        demonstrate_features()
    else:
        print("Personal Finance Tracker - Sample Usage\n")
        print("Options:")
        print("  --create-sample  : Create sample transaction data")
        print("  --demo          : Run feature demonstration")
        print("\nExample:")
        print("  python sample_usage.py --create-sample")
        print("  python sample_usage.py --demo")


if __name__ == "__main__":
    main()
