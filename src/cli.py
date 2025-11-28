"""
Command Line Interface
Main CLI for Personal Finance Tracker
"""

from datetime import datetime
from colorama import init, Fore, Style
from tabulate import tabulate

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class CLI:
    """Command-line interface for the finance tracker"""

    def __init__(self, transaction_manager, report_generator, csv_exporter, visualizer):
        """Initialize CLI with all required components"""
        self.tm = transaction_manager
        self.rg = report_generator
        self.ce = csv_exporter
        self.viz = visualizer

    def print_header(self):
        """Print application header"""
        print(Fore.CYAN + Style.BRIGHT + "\n" + "=" * 70)
        print(Fore.CYAN + Style.BRIGHT + "  PERSONAL FINANCE TRACKER")
        print(Fore.CYAN + Style.BRIGHT + "  Powered by Apache Spark")
        print(Fore.CYAN + Style.BRIGHT + "=" * 70 + Style.RESET_ALL)

    def print_menu(self):
        """Print main menu"""
        menu_items = [
            ["1", "Add Transaction"],
            ["2", "Remove Transaction"],
            ["3", "List Transactions"],
            ["4", "Search Transactions"],
            ["5", "View Balance"],
            ["6", "Generate Monthly Report"],
            ["7", "Generate Yearly Report"],
            ["8", "Category Report"],
            ["9", "Export to CSV"],
            ["10", "Create Visualizations"],
            ["11", "View Categories"],
            ["0", "Save & Exit"]
        ]

        print("\n" + Fore.YELLOW + Style.BRIGHT + "MAIN MENU:" + Style.RESET_ALL)
        print(tabulate(menu_items, tablefmt="simple"))

    def add_transaction_menu(self):
        """Handle adding a new transaction"""
        print("\n" + Fore.GREEN + Style.BRIGHT + "ADD TRANSACTION" + Style.RESET_ALL)

        # Select type
        print("\nTransaction Type:")
        print("1. Income")
        print("2. Expense")
        type_choice = input("Select (1-2): ").strip()

        if type_choice == "1":
            transaction_type = "income"
            categories = self.tm.INCOME_CATEGORIES
        elif type_choice == "2":
            transaction_type = "expense"
            categories = self.tm.EXPENSE_CATEGORIES
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
            return

        # Select category
        print(f"\n{transaction_type.capitalize()} Categories:")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        print(f"{len(categories) + 1}. Custom Category")

        cat_choice = input(f"Select (1-{len(categories) + 1}): ").strip()

        try:
            cat_idx = int(cat_choice) - 1
            if 0 <= cat_idx < len(categories):
                category = categories[cat_idx]
            elif cat_idx == len(categories):
                category = input("Enter custom category: ").strip()
            else:
                print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
                return
        except ValueError:
            print(Fore.RED + "Invalid input!" + Style.RESET_ALL)
            return

        # Enter amount
        try:
            amount = float(input("Enter amount: $").strip())
        except ValueError:
            print(Fore.RED + "Invalid amount!" + Style.RESET_ALL)
            return

        # Enter description (optional)
        description = input("Enter description (optional): ").strip()

        # Enter date (optional)
        date_input = input("Enter date (YYYY-MM-DD, or press Enter for today): ").strip()
        date = date_input if date_input else None

        # Add transaction
        self.tm.add_transaction(transaction_type, category, amount, description, date)

    def remove_transaction_menu(self):
        """Handle removing a transaction"""
        print("\n" + Fore.RED + Style.BRIGHT + "REMOVE TRANSACTION" + Style.RESET_ALL)

        # First show recent transactions
        print("\nRecent transactions:")
        self.tm.list_transactions(limit=10)

        transaction_id = input("\nEnter transaction ID to remove (or 'cancel' to go back): ").strip()

        if transaction_id.lower() == 'cancel':
            return

        self.tm.remove_transaction(transaction_id)

    def list_transactions_menu(self):
        """Handle listing transactions"""
        print("\n" + Fore.CYAN + Style.BRIGHT + "LIST TRANSACTIONS" + Style.RESET_ALL)

        print("\nFilter Options:")
        print("1. All Transactions")
        print("2. Income Only")
        print("3. Expenses Only")
        print("4. By Category")

        choice = input("Select (1-4): ").strip()

        if choice == "1":
            limit_input = input("Enter number of transactions to show (or press Enter for all): ").strip()
            limit = int(limit_input) if limit_input else None
            self.tm.list_transactions(limit=limit)
        elif choice == "2":
            self.tm.list_transactions(transaction_type="income")
        elif choice == "3":
            self.tm.list_transactions(transaction_type="expense")
        elif choice == "4":
            category = input("Enter category: ").strip()
            self.tm.list_transactions(category=category)
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

    def search_transactions_menu(self):
        """Handle searching transactions"""
        print("\n" + Fore.CYAN + Style.BRIGHT + "SEARCH TRANSACTIONS" + Style.RESET_ALL)
        keyword = input("\nEnter search keyword: ").strip()
        self.tm.search_transactions(keyword)

    def view_balance_menu(self):
        """Display current balance"""
        balance = self.tm.get_balance()
        print("\n" + Fore.CYAN + Style.BRIGHT + "CURRENT BALANCE" + Style.RESET_ALL)
        if balance >= 0:
            print(Fore.GREEN + f"\n${balance:,.2f}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"\n-${abs(balance):,.2f}" + Style.RESET_ALL)

    def monthly_report_menu(self):
        """Generate monthly report"""
        print("\n" + Fore.MAGENTA + Style.BRIGHT + "MONTHLY REPORT" + Style.RESET_ALL)

        year_input = input("Enter year (or press Enter for current year): ").strip()
        month_input = input("Enter month (1-12, or press Enter for current month): ").strip()

        try:
            year = int(year_input) if year_input else None
            month = int(month_input) if month_input else None
            self.rg.monthly_summary(year, month)
        except ValueError:
            print(Fore.RED + "Invalid input!" + Style.RESET_ALL)

    def yearly_report_menu(self):
        """Generate yearly report"""
        print("\n" + Fore.MAGENTA + Style.BRIGHT + "YEARLY REPORT" + Style.RESET_ALL)

        year_input = input("Enter year (or press Enter for current year): ").strip()

        try:
            year = int(year_input) if year_input else None
            self.rg.yearly_summary(year)
        except ValueError:
            print(Fore.RED + "Invalid input!" + Style.RESET_ALL)

    def category_report_menu(self):
        """Generate category report"""
        print("\n" + Fore.MAGENTA + Style.BRIGHT + "CATEGORY REPORT" + Style.RESET_ALL)

        category = input("\nEnter category name: ").strip()
        self.rg.category_report(category)

    def export_csv_menu(self):
        """Handle CSV export"""
        print("\n" + Fore.BLUE + Style.BRIGHT + "EXPORT TO CSV" + Style.RESET_ALL)

        print("\nExport Options:")
        print("1. All Transactions")
        print("2. Income Only")
        print("3. Expenses Only")
        print("4. By Category")
        print("5. Date Range")
        print("6. Monthly Summary")

        choice = input("Select (1-6): ").strip()

        if choice == "1":
            self.ce.export_all_transactions()
        elif choice == "2":
            self.ce.export_by_type("income")
        elif choice == "3":
            self.ce.export_by_type("expense")
        elif choice == "4":
            category = input("Enter category: ").strip()
            self.ce.export_by_category(category)
        elif choice == "5":
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            self.ce.export_date_range(start_date, end_date)
        elif choice == "6":
            year = int(input("Enter year: ").strip())
            month = int(input("Enter month (1-12): ").strip())
            self.ce.export_monthly_summary(year, month)
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

    def visualizations_menu(self):
        """Handle visualizations"""
        print("\n" + Fore.MAGENTA + Style.BRIGHT + "CREATE VISUALIZATIONS" + Style.RESET_ALL)

        print("\nVisualization Options:")
        print("1. Expense Pie Chart")
        print("2. Income vs Expenses Bar Chart")
        print("3. Monthly Trend Line Chart")
        print("4. Category Comparison")
        print("5. Spending Pattern (by category)")
        print("6. Generate All Visualizations")

        choice = input("Select (1-6): ").strip()

        if choice == "1":
            self.viz.plot_expense_by_category()
        elif choice == "2":
            self.viz.plot_income_vs_expenses()
        elif choice == "3":
            year_input = input("Enter year (or press Enter for current year): ").strip()
            year = int(year_input) if year_input else None
            self.viz.plot_monthly_trend(year)
        elif choice == "4":
            self.viz.plot_category_comparison()
        elif choice == "5":
            category = input("Enter category: ").strip()
            self.viz.plot_spending_pattern(category)
        elif choice == "6":
            print("\nGenerating all visualizations...")
            self.viz.plot_expense_by_category()
            self.viz.plot_income_vs_expenses()
            self.viz.plot_monthly_trend()
            self.viz.plot_category_comparison()
            print(Fore.GREEN + "\n✓ All visualizations created!" + Style.RESET_ALL)
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

    def view_categories_menu(self):
        """Display available categories"""
        print("\n" + Fore.CYAN + Style.BRIGHT + "AVAILABLE CATEGORIES" + Style.RESET_ALL)

        print("\n" + Fore.GREEN + "Income Categories:" + Style.RESET_ALL)
        for i, cat in enumerate(self.tm.INCOME_CATEGORIES, 1):
            print(f"  {i}. {cat}")

        print("\n" + Fore.RED + "Expense Categories:" + Style.RESET_ALL)
        for i, cat in enumerate(self.tm.EXPENSE_CATEGORIES, 1):
            print(f"  {i}. {cat}")

    def run(self):
        """Main CLI loop"""
        self.print_header()

        while True:
            self.print_menu()
            choice = input("\nEnter your choice: ").strip()

            if choice == "1":
                self.add_transaction_menu()
            elif choice == "2":
                self.remove_transaction_menu()
            elif choice == "3":
                self.list_transactions_menu()
            elif choice == "4":
                self.search_transactions_menu()
            elif choice == "5":
                self.view_balance_menu()
            elif choice == "6":
                self.monthly_report_menu()
            elif choice == "7":
                self.yearly_report_menu()
            elif choice == "8":
                self.category_report_menu()
            elif choice == "9":
                self.export_csv_menu()
            elif choice == "10":
                self.visualizations_menu()
            elif choice == "11":
                self.view_categories_menu()
            elif choice == "0":
                print("\n" + Fore.YELLOW + "Saving data..." + Style.RESET_ALL)
                break
            else:
                print(Fore.RED + "\nInvalid choice! Please try again." + Style.RESET_ALL)

            input("\nPress Enter to continue...")
