"""
Report Generator
Generates financial reports and summaries
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pyspark.sql import functions as F
from tabulate import tabulate


class ReportGenerator:
    """Generates various financial reports using Spark"""

    def __init__(self, spark_backend):
        """Initialize with Spark backend"""
        self.backend = spark_backend

    def monthly_summary(self, year=None, month=None):
        """Generate monthly summary report"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month

        # Create date range for the month
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_year = year + 1
            end_month = 1
        else:
            end_year = year
            end_month = month + 1
        end_date = f"{end_year}-{end_month:02d}-01"

        df = self.backend.filter_by_date_range(start_date, end_date)

        if df.count() == 0:
            print(f"\nNo transactions found for {year}-{month:02d}")
            return

        # Calculate totals
        income_df = df.filter(df.type == "income")
        expense_df = df.filter(df.type == "expense")

        total_income = income_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        total_expenses = expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        net_savings = total_income - total_expenses

        # Category breakdown
        expense_by_category = expense_df.groupBy("category").agg(
            F.sum("amount").alias("total"),
            F.count("*").alias("count")
        ).orderBy("total", ascending=False).collect()

        income_by_category = income_df.groupBy("category").agg(
            F.sum("amount").alias("total"),
            F.count("*").alias("count")
        ).orderBy("total", ascending=False).collect()

        # Display report
        print(f"\n{'='*60}")
        print(f"  MONTHLY FINANCIAL REPORT - {datetime(year, month, 1).strftime('%B %Y')}")
        print(f"{'='*60}\n")

        print(f"Total Income:    ${total_income:,.2f}")
        print(f"Total Expenses:  ${total_expenses:,.2f}")
        print(f"Net Savings:     ${net_savings:,.2f}")
        print(f"Savings Rate:    {(net_savings/total_income*100 if total_income > 0 else 0):.1f}%\n")

        if len(expense_by_category) > 0:
            print("EXPENSES BY CATEGORY:")
            print("-" * 60)
            expense_data = []
            for row in expense_by_category:
                percentage = (row.total / total_expenses * 100) if total_expenses > 0 else 0
                expense_data.append([
                    row.category,
                    f"${row.total:,.2f}",
                    f"{percentage:.1f}%",
                    row.count
                ])
            print(tabulate(expense_data, headers=["Category", "Amount", "% of Total", "Count"], tablefmt="simple"))
            print()

        if len(income_by_category) > 0:
            print("INCOME BY CATEGORY:")
            print("-" * 60)
            income_data = []
            for row in income_by_category:
                percentage = (row.total / total_income * 100) if total_income > 0 else 0
                income_data.append([
                    row.category,
                    f"${row.total:,.2f}",
                    f"{percentage:.1f}%",
                    row.count
                ])
            print(tabulate(income_data, headers=["Category", "Amount", "% of Total", "Count"], tablefmt="simple"))
            print()

    def yearly_summary(self, year=None):
        """Generate yearly summary report"""
        if year is None:
            year = datetime.now().year

        start_date = f"{year}-01-01"
        end_date = f"{year + 1}-01-01"

        df = self.backend.filter_by_date_range(start_date, end_date)

        if df.count() == 0:
            print(f"\nNo transactions found for {year}")
            return

        # Calculate totals
        income_df = df.filter(df.type == "income")
        expense_df = df.filter(df.type == "expense")

        total_income = income_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        total_expenses = expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        net_savings = total_income - total_expenses

        # Monthly breakdown
        monthly_data = []
        for month in range(1, 13):
            month_start = f"{year}-{month:02d}-01"
            if month == 12:
                month_end = f"{year + 1}-01-01"
            else:
                month_end = f"{year}-{month + 1:02d}-01"

            month_df = self.backend.filter_by_date_range(month_start, month_end)

            if month_df.count() > 0:
                month_income_df = month_df.filter(month_df.type == "income")
                month_expense_df = month_df.filter(month_df.type == "expense")

                month_income = month_income_df.agg(F.sum("amount")).collect()[0][0] or 0.0
                month_expense = month_expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0
                month_savings = month_income - month_expense

                monthly_data.append([
                    datetime(year, month, 1).strftime("%B"),
                    f"${month_income:,.2f}",
                    f"${month_expense:,.2f}",
                    f"${month_savings:,.2f}"
                ])

        # Category breakdown
        expense_by_category = expense_df.groupBy("category").agg(
            F.sum("amount").alias("total")
        ).orderBy("total", ascending=False).collect()

        # Display report
        print(f"\n{'='*70}")
        print(f"  YEARLY FINANCIAL REPORT - {year}")
        print(f"{'='*70}\n")

        print(f"Total Income:    ${total_income:,.2f}")
        print(f"Total Expenses:  ${total_expenses:,.2f}")
        print(f"Net Savings:     ${net_savings:,.2f}")
        print(f"Savings Rate:    {(net_savings/total_income*100 if total_income > 0 else 0):.1f}%\n")

        if len(monthly_data) > 0:
            print("MONTHLY BREAKDOWN:")
            print("-" * 70)
            print(tabulate(monthly_data, headers=["Month", "Income", "Expenses", "Savings"], tablefmt="simple"))
            print()

        if len(expense_by_category) > 0:
            print("TOP EXPENSE CATEGORIES:")
            print("-" * 70)
            expense_data = []
            for row in expense_by_category[:10]:
                percentage = (row.total / total_expenses * 100) if total_expenses > 0 else 0
                expense_data.append([
                    row.category,
                    f"${row.total:,.2f}",
                    f"{percentage:.1f}%"
                ])
            print(tabulate(expense_data, headers=["Category", "Amount", "% of Total"], tablefmt="simple"))
            print()

    def category_report(self, category):
        """Generate report for a specific category"""
        df = self.backend.filter_by_category(category)

        if df.count() == 0:
            print(f"\nNo transactions found for category: {category}")
            return

        # Calculate statistics
        total = df.agg(F.sum("amount")).collect()[0][0] or 0.0
        avg = df.agg(F.avg("amount")).collect()[0][0] or 0.0
        count = df.count()
        max_amount = df.agg(F.max("amount")).collect()[0][0] or 0.0
        min_amount = df.agg(F.min("amount")).collect()[0][0] or 0.0

        # Get recent transactions
        recent = df.orderBy("date", ascending=False).limit(10).toPandas()

        # Display report
        print(f"\n{'='*60}")
        print(f"  CATEGORY REPORT: {category}")
        print(f"{'='*60}\n")

        print(f"Total Transactions: {count}")
        print(f"Total Amount:       ${total:,.2f}")
        print(f"Average Amount:     ${avg:,.2f}")
        print(f"Largest Transaction: ${max_amount:,.2f}")
        print(f"Smallest Transaction: ${min_amount:,.2f}\n")

        if len(recent) > 0:
            print("RECENT TRANSACTIONS:")
            print("-" * 60)
            transaction_data = []
            for _, row in recent.iterrows():
                transaction_data.append([
                    row['date'],
                    row['type'].capitalize(),
                    f"${row['amount']:.2f}",
                    row['description'][:40] if row['description'] else ""
                ])
            print(tabulate(transaction_data, headers=["Date", "Type", "Amount", "Description"], tablefmt="simple"))
            print()

    def custom_date_range_report(self, start_date, end_date):
        """Generate report for custom date range"""
        df = self.backend.filter_by_date_range(start_date, end_date)

        if df.count() == 0:
            print(f"\nNo transactions found between {start_date} and {end_date}")
            return

        # Calculate totals
        income_df = df.filter(df.type == "income")
        expense_df = df.filter(df.type == "expense")

        total_income = income_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        total_expenses = expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        net_savings = total_income - total_expenses

        # Category breakdown
        expense_by_category = expense_df.groupBy("category").agg(
            F.sum("amount").alias("total")
        ).orderBy("total", ascending=False).collect()

        # Display report
        print(f"\n{'='*60}")
        print(f"  CUSTOM REPORT: {start_date} to {end_date}")
        print(f"{'='*60}\n")

        print(f"Total Income:    ${total_income:,.2f}")
        print(f"Total Expenses:  ${total_expenses:,.2f}")
        print(f"Net Savings:     ${net_savings:,.2f}\n")

        if len(expense_by_category) > 0:
            print("EXPENSES BY CATEGORY:")
            print("-" * 60)
            expense_data = []
            for row in expense_by_category:
                percentage = (row.total / total_expenses * 100) if total_expenses > 0 else 0
                expense_data.append([
                    row.category,
                    f"${row.total:,.2f}",
                    f"{percentage:.1f}%"
                ])
            print(tabulate(expense_data, headers=["Category", "Amount", "% of Total"], tablefmt="simple"))
            print()
