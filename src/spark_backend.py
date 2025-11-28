"""
Apache Spark Backend for Personal Finance Tracker
Handles data storage and processing using PySpark
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from pyspark.sql import DataFrame
import os
from datetime import datetime


class SparkBackend:
    """Manages Spark session and data operations"""

    def __init__(self, app_name="PersonalFinanceTracker", data_path="data/transactions"):
        """Initialize Spark session and setup data storage"""
        self.app_name = app_name
        self.data_path = data_path
        self.spark = None
        self.transactions_df = None
        self._init_spark()
        self._setup_schema()

    def _init_spark(self):
        """Initialize or get Spark session"""
        self.spark = SparkSession.builder \
            .appName(self.app_name) \
            .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()

        # Set log level to reduce verbosity
        self.spark.sparkContext.setLogLevel("ERROR")

    def _setup_schema(self):
        """Define schema for transactions"""
        self.schema = StructType([
            StructField("transaction_id", StringType(), False),
            StructField("date", StringType(), False),
            StructField("type", StringType(), False),  # income or expense
            StructField("category", StringType(), False),
            StructField("amount", DoubleType(), False),
            StructField("description", StringType(), True),
            StructField("created_at", StringType(), False)
        ])

    def load_data(self):
        """Load existing transaction data from parquet files"""
        try:
            if os.path.exists(self.data_path) and os.listdir(self.data_path):
                self.transactions_df = self.spark.read.parquet(self.data_path)
                print(f"Loaded {self.transactions_df.count()} transactions from storage.")
            else:
                # Create empty DataFrame with schema
                self.transactions_df = self.spark.createDataFrame([], self.schema)
                print("No existing data found. Starting fresh.")
        except Exception as e:
            print(f"Error loading data: {e}")
            self.transactions_df = self.spark.createDataFrame([], self.schema)

    def save_data(self):
        """Save transaction data to parquet files"""
        try:
            if self.transactions_df is not None and self.transactions_df.count() > 0:
                # Create directory if it doesn't exist
                os.makedirs(self.data_path, exist_ok=True)

                # Save as parquet (overwrite mode)
                self.transactions_df.write.mode("overwrite").parquet(self.data_path)
                print("Data saved successfully.")
            else:
                print("No data to save.")
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_transaction(self, transaction_data):
        """Add a new transaction to the DataFrame"""
        try:
            new_transaction_df = self.spark.createDataFrame([transaction_data], self.schema)

            if self.transactions_df.count() == 0:
                self.transactions_df = new_transaction_df
            else:
                self.transactions_df = self.transactions_df.union(new_transaction_df)

            return True
        except Exception as e:
            print(f"Error adding transaction: {e}")
            return False

    def remove_transaction(self, transaction_id):
        """Remove a transaction by ID"""
        try:
            if self.transactions_df is None or self.transactions_df.count() == 0:
                return False

            initial_count = self.transactions_df.count()
            self.transactions_df = self.transactions_df.filter(
                self.transactions_df.transaction_id != transaction_id
            )

            return self.transactions_df.count() < initial_count
        except Exception as e:
            print(f"Error removing transaction: {e}")
            return False

    def get_all_transactions(self):
        """Get all transactions as a DataFrame"""
        return self.transactions_df

    def filter_by_date_range(self, start_date, end_date):
        """Filter transactions by date range"""
        try:
            return self.transactions_df.filter(
                (self.transactions_df.date >= start_date) &
                (self.transactions_df.date <= end_date)
            )
        except Exception as e:
            print(f"Error filtering by date: {e}")
            return self.spark.createDataFrame([], self.schema)

    def filter_by_category(self, category):
        """Filter transactions by category"""
        try:
            return self.transactions_df.filter(
                self.transactions_df.category == category
            )
        except Exception as e:
            print(f"Error filtering by category: {e}")
            return self.spark.createDataFrame([], self.schema)

    def filter_by_type(self, transaction_type):
        """Filter transactions by type (income/expense)"""
        try:
            return self.transactions_df.filter(
                self.transactions_df.type == transaction_type
            )
        except Exception as e:
            print(f"Error filtering by type: {e}")
            return self.spark.createDataFrame([], self.schema)

    def get_categories(self):
        """Get all unique categories"""
        try:
            if self.transactions_df.count() > 0:
                categories = self.transactions_df.select("category").distinct().collect()
                return [row.category for row in categories]
            return []
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def stop(self):
        """Stop Spark session"""
        if self.spark:
            self.spark.stop()
            print("Spark session stopped.")
