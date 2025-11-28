"""
Data Visualizer
Creates visualizations using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from datetime import datetime
from pyspark.sql import functions as F
import os


class DataVisualizer:
    """Creates various data visualizations"""

    def __init__(self, spark_backend):
        """Initialize with Spark backend"""
        self.backend = spark_backend

    def plot_expense_by_category(self, output_path=None):
        """Create a pie chart of expenses by category"""
        df = self.backend.filter_by_type("expense")

        if df is None or df.count() == 0:
            print("\nNo expense data available for visualization.")
            return False

        # Group by category
        category_totals = df.groupBy("category").agg(
            F.sum("amount").alias("total")
        ).orderBy("total", ascending=False).collect()

        if len(category_totals) == 0:
            print("\nNo expense categories to visualize.")
            return False

        # Prepare data
        categories = [row.category for row in category_totals]
        amounts = [row.total for row in category_totals]

        # Create pie chart
        plt.figure(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(categories)))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, colors=colors)
        plt.title('Expenses by Category', fontsize=16, fontweight='bold')
        plt.axis('equal')

        # Save plot
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"visualizations/expense_by_category_{timestamp}.png"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n✓ Visualization saved to: {output_path}")
        return True

    def plot_income_vs_expenses(self, output_path=None):
        """Create a bar chart comparing income vs expenses"""
        df = self.backend.get_all_transactions()

        if df is None or df.count() == 0:
            print("\nNo transaction data available for visualization.")
            return False

        # Calculate totals
        income_total = df.filter(df.type == "income").agg(F.sum("amount")).collect()[0][0] or 0.0
        expense_total = df.filter(df.type == "expense").agg(F.sum("amount")).collect()[0][0] or 0.0

        # Create bar chart
        plt.figure(figsize=(10, 6))
        categories = ['Income', 'Expenses', 'Net Savings']
        values = [income_total, expense_total, income_total - expense_total]
        colors = ['#2ecc71', '#e74c3c', '#3498db']

        bars = plt.bar(categories, values, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:,.0f}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')

        plt.title('Income vs Expenses Overview', fontsize=16, fontweight='bold')
        plt.ylabel('Amount ($)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)

        # Save plot
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"visualizations/income_vs_expenses_{timestamp}.png"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n✓ Visualization saved to: {output_path}")
        return True

    def plot_monthly_trend(self, year=None, output_path=None):
        """Create a line chart showing monthly income and expense trends"""
        if year is None:
            year = datetime.now().year

        start_date = f"{year}-01-01"
        end_date = f"{year + 1}-01-01"

        df = self.backend.filter_by_date_range(start_date, end_date)

        if df is None or df.count() == 0:
            print(f"\nNo transaction data available for {year}.")
            return False

        # Collect monthly data
        months = []
        income_data = []
        expense_data = []

        for month in range(1, 13):
            month_start = f"{year}-{month:02d}-01"
            if month == 12:
                month_end = f"{year + 1}-01-01"
            else:
                month_end = f"{year}-{month + 1:02d}-01"

            month_df = self.backend.filter_by_date_range(month_start, month_end)

            if month_df.count() > 0:
                month_income = month_df.filter(month_df.type == "income").agg(F.sum("amount")).collect()[0][0] or 0.0
                month_expense = month_df.filter(month_df.type == "expense").agg(F.sum("amount")).collect()[0][0] or 0.0
            else:
                month_income = 0.0
                month_expense = 0.0

            months.append(datetime(year, month, 1).strftime("%b"))
            income_data.append(month_income)
            expense_data.append(month_expense)

        # Create line chart
        plt.figure(figsize=(12, 6))
        plt.plot(months, income_data, marker='o', linewidth=2, label='Income', color='#2ecc71')
        plt.plot(months, expense_data, marker='s', linewidth=2, label='Expenses', color='#e74c3c')

        plt.title(f'Monthly Income vs Expenses Trend - {year}', fontsize=16, fontweight='bold')
        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)

        # Save plot
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"visualizations/monthly_trend_{year}_{timestamp}.png"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n✓ Visualization saved to: {output_path}")
        return True

    def plot_category_comparison(self, output_path=None):
        """Create a horizontal bar chart comparing all categories"""
        df = self.backend.get_all_transactions()

        if df is None or df.count() == 0:
            print("\nNo transaction data available for visualization.")
            return False

        # Group by type and category
        category_totals = df.groupBy("type", "category").agg(
            F.sum("amount").alias("total")
        ).orderBy("total", ascending=False).collect()

        if len(category_totals) == 0:
            print("\nNo categories to visualize.")
            return False

        # Prepare data
        income_categories = []
        income_amounts = []
        expense_categories = []
        expense_amounts = []

        for row in category_totals:
            if row.type == "income":
                income_categories.append(row.category)
                income_amounts.append(row.total)
            else:
                expense_categories.append(row.category)
                expense_amounts.append(row.total)

        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

        # Income chart
        if income_categories:
            y_pos = range(len(income_categories))
            ax1.barh(y_pos, income_amounts, color='#2ecc71', alpha=0.7)
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(income_categories)
            ax1.set_xlabel('Amount ($)', fontsize=10)
            ax1.set_title('Income by Category', fontsize=14, fontweight='bold')
            ax1.grid(axis='x', alpha=0.3)

            # Add value labels
            for i, v in enumerate(income_amounts):
                ax1.text(v, i, f' ${v:,.0f}', va='center', fontsize=9)

        # Expense chart
        if expense_categories:
            y_pos = range(len(expense_categories))
            ax2.barh(y_pos, expense_amounts, color='#e74c3c', alpha=0.7)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(expense_categories)
            ax2.set_xlabel('Amount ($)', fontsize=10)
            ax2.set_title('Expenses by Category', fontsize=14, fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)

            # Add value labels
            for i, v in enumerate(expense_amounts):
                ax2.text(v, i, f' ${v:,.0f}', va='center', fontsize=9)

        plt.tight_layout()

        # Save plot
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"visualizations/category_comparison_{timestamp}.png"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n✓ Visualization saved to: {output_path}")
        return True

    def plot_spending_pattern(self, category, output_path=None):
        """Create a timeline chart for a specific category"""
        df = self.backend.filter_by_category(category)

        if df is None or df.count() == 0:
            print(f"\nNo transactions found for category: {category}")
            return False

        # Convert to pandas for easier plotting
        pandas_df = df.orderBy("date").toPandas()

        # Create scatter plot
        plt.figure(figsize=(12, 6))
        colors = ['#2ecc71' if t == 'income' else '#e74c3c' for t in pandas_df['type']]
        plt.scatter(pandas_df['date'], pandas_df['amount'], c=colors, alpha=0.6, s=100, edgecolors='black')

        plt.title(f'Spending Pattern: {category}', fontsize=16, fontweight='bold')
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Amount ($)', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2ecc71', label='Income'),
            Patch(facecolor='#e74c3c', label='Expense')
        ]
        plt.legend(handles=legend_elements, fontsize=10)

        # Save plot
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_category = category.replace(" ", "_").replace("&", "and")
            output_path = f"visualizations/spending_pattern_{safe_category}_{timestamp}.png"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"\n✓ Visualization saved to: {output_path}")
        return True
