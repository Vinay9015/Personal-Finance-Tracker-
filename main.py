#!/usr/bin/env python3
"""
Personal Finance Tracker - Main Entry Point
A command-line application to track income, expenses, and generate financial reports
Powered by Apache Spark
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
from cli import CLI


def main():
    """Main entry point for the application"""
    print("Initializing Personal Finance Tracker...")
    print("Starting Apache Spark...")

    # Initialize Spark backend
    backend = SparkBackend(
        app_name="PersonalFinanceTracker",
        data_path="data/transactions"
    )

    # Load existing data
    backend.load_data()

    # Initialize components
    transaction_manager = TransactionManager(backend)
    report_generator = ReportGenerator(backend)
    csv_exporter = CSVExporter(backend)
    visualizer = DataVisualizer(backend)

    # Initialize and run CLI
    cli = CLI(transaction_manager, report_generator, csv_exporter, visualizer)

    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Save data and cleanup
        print("\nSaving data...")
        backend.save_data()
        print("Stopping Spark session...")
        backend.stop()
        print("\nThank you for using Personal Finance Tracker!")
        print("Your data has been saved successfully.\n")


if __name__ == "__main__":
    main()
