"""
CSV Exporter
Exports transaction data to CSV format
"""

import os
from datetime import datetime


class CSVExporter:
    """Handles CSV export functionality"""

    def __init__(self, spark_backend):
        """Initialize with Spark backend"""
        self.backend = spark_backend

    def export_all_transactions(self, output_path=None):
        """Export all transactions to CSV"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/transactions_{timestamp}.csv"

        df = self.backend.get_all_transactions()

        if df is None or df.count() == 0:
            print("\nNo transactions to export.")
            return False

        try:
            # Create exports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert to Pandas and export to CSV
            pandas_df = df.orderBy("date", ascending=False).toPandas()
            pandas_df.to_csv(output_path, index=False)

            print(f"\n✓ Successfully exported {len(pandas_df)} transactions to:")
            print(f"  {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error exporting to CSV: {e}")
            return False

    def export_by_type(self, transaction_type, output_path=None):
        """Export transactions filtered by type"""
        if transaction_type not in ["income", "expense"]:
            print("Error: Transaction type must be 'income' or 'expense'")
            return False

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/{transaction_type}_{timestamp}.csv"

        df = self.backend.filter_by_type(transaction_type)

        if df is None or df.count() == 0:
            print(f"\nNo {transaction_type} transactions to export.")
            return False

        try:
            # Create exports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert to Pandas and export to CSV
            pandas_df = df.orderBy("date", ascending=False).toPandas()
            pandas_df.to_csv(output_path, index=False)

            print(f"\n✓ Successfully exported {len(pandas_df)} {transaction_type} transactions to:")
            print(f"  {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error exporting to CSV: {e}")
            return False

    def export_by_category(self, category, output_path=None):
        """Export transactions filtered by category"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_category = category.replace(" ", "_").replace("&", "and")
            output_path = f"exports/{safe_category}_{timestamp}.csv"

        df = self.backend.filter_by_category(category)

        if df is None or df.count() == 0:
            print(f"\nNo transactions in category '{category}' to export.")
            return False

        try:
            # Create exports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert to Pandas and export to CSV
            pandas_df = df.orderBy("date", ascending=False).toPandas()
            pandas_df.to_csv(output_path, index=False)

            print(f"\n✓ Successfully exported {len(pandas_df)} transactions from '{category}' to:")
            print(f"  {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error exporting to CSV: {e}")
            return False

    def export_date_range(self, start_date, end_date, output_path=None):
        """Export transactions within a date range"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"exports/transactions_{start_date}_to_{end_date}_{timestamp}.csv"

        df = self.backend.filter_by_date_range(start_date, end_date)

        if df is None or df.count() == 0:
            print(f"\nNo transactions between {start_date} and {end_date} to export.")
            return False

        try:
            # Create exports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Convert to Pandas and export to CSV
            pandas_df = df.orderBy("date", ascending=False).toPandas()
            pandas_df.to_csv(output_path, index=False)

            print(f"\n✓ Successfully exported {len(pandas_df)} transactions to:")
            print(f"  {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error exporting to CSV: {e}")
            return False

    def export_monthly_summary(self, year, month, output_path=None):
        """Export monthly summary as CSV"""
        if output_path is None:
            output_path = f"exports/monthly_summary_{year}_{month:02d}.csv"

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

        if df is None or df.count() == 0:
            print(f"\nNo transactions found for {year}-{month:02d}")
            return False

        try:
            # Create exports directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Get category summary using Spark
            from pyspark.sql import functions as F

            summary_df = df.groupBy("type", "category").agg(
                F.sum("amount").alias("total_amount"),
                F.count("*").alias("transaction_count"),
                F.avg("amount").alias("average_amount")
            ).orderBy("type", "total_amount", ascending=[True, False])

            # Convert to Pandas and export
            pandas_df = summary_df.toPandas()
            pandas_df.to_csv(output_path, index=False)

            print(f"\n✓ Successfully exported monthly summary to:")
            print(f"  {output_path}")
            return True
        except Exception as e:
            print(f"\n✗ Error exporting monthly summary: {e}")
            return False
