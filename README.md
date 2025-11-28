# Personal Finance Tracker

A modern web application and command-line tool to track income, expenses, and generate comprehensive financial reports. Built with Flask, Apache Spark, and Chart.js for powerful data processing and beautiful visualizations.

## 🌐 New Web Interface Available!

Access your finances through a beautiful, responsive web interface with:
- **Interactive Dashboard** with real-time statistics
- **Chart.js Visualizations** with dynamic, interactive charts
- **Easy Transaction Management** with intuitive forms
- **Responsive Design** that works on desktop and mobile
- **Real-time Updates** without page refreshes

## Features

### Core Functionality
- **Transaction Management**: Add and remove income/expense transactions
- **Smart Categorization**: Predefined categories for both income and expenses
- **Advanced Search**: Search transactions by keywords, categories, or date ranges
- **Real-time Balance**: Track your current financial balance

### Reporting & Analytics
- **Monthly Reports**: Detailed breakdown of income, expenses, and savings by month
- **Yearly Reports**: Comprehensive annual financial summaries with monthly trends
- **Category Reports**: Deep dive into specific spending categories
- **Custom Date Range Reports**: Analyze any time period

### Data Export
- **CSV Export**: Export transactions in various formats (all, by type, by category, date range)
- **Monthly Summary Export**: Export aggregated monthly data for external analysis

### Visualizations
- **Expense Pie Chart**: Visual breakdown of expenses by category
- **Income vs Expenses**: Bar chart comparison
- **Monthly Trends**: Line charts showing financial trends over time
- **Category Comparison**: Side-by-side comparison of all categories
- **Spending Patterns**: Timeline analysis for specific categories

## Technical Stack

### Backend
- **Apache Spark (PySpark)**: Distributed data processing backend
- **Flask**: Web framework for the web application
- **Pandas**: Data manipulation and analysis
- **Matplotlib**: Data visualization (CLI)

### Frontend (Web App)
- **HTML5 & CSS3**: Modern, responsive UI
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Interactive data visualizations
- **Font Awesome**: Icon library

### CLI Tools
- **Colorama**: Colored terminal output
- **Tabulate**: Beautiful table formatting

## Installation

### Prerequisites
- Python 3.8 or higher
- Java 11
- pip package manager

**Note:** The application works with Java 11
### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Personal-Finance-Tracker-
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application (Recommended)

Run the modern web interface:
```bash
python app.py
```

Then open your browser and navigate to: **http://localhost:5001**

### Command-Line Application

Run the CLI version:
```bash
python main.py
```

### Main Menu Options

1. **Add Transaction**: Record new income or expense
2. **Remove Transaction**: Delete a transaction by ID
3. **List Transactions**: View all or filtered transactions
4. **Search Transactions**: Find transactions by keyword
5. **View Balance**: Check current balance (income - expenses)
6. **Generate Monthly Report**: Detailed monthly financial analysis
7. **Generate Yearly Report**: Comprehensive annual overview
8. **Category Report**: Analyze spending in a specific category
9. **Export to CSV**: Export data in various formats
10. **Create Visualizations**: Generate charts and graphs
11. **View Categories**: See all available categories
0. **Save & Exit**: Save data and close the application

### Transaction Categories

#### Income Categories
- Salary
- Freelance
- Business
- Investment
- Gift
- Other Income

#### Expense Categories
- Food & Dining
- Transportation
- Shopping
- Entertainment
- Bills & Utilities
- Healthcare
- Education
- Travel
- Groceries
- Other Expenses

## Data Storage

- Transactions are stored in Parquet format using Apache Spark
- Default storage location: `data/transactions/`
- Exports are saved to: `exports/`
- Visualizations are saved to: `visualizations/`

## Project Structure

```
Personal-Finance-Tracker-/
├── app.py                     # Web application entry point (Flask)
├── main.py                    # CLI application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules
├── src/
│   ├── __init__.py
│   ├── spark_backend.py         # Spark session and data operations
│   ├── transaction_manager.py   # Transaction CRUD operations
│   ├── report_generator.py     # Report generation logic
│   ├── csv_exporter.py         # CSV export functionality
│   ├── visualizer.py           # Data visualization with matplotlib
│   └── cli.py                  # Command-line interface
├── templates/                # HTML templates for web app
│   ├── base.html               # Base template
│   ├── index.html              # Dashboard page
│   ├── transactions.html       # Transactions page
│   ├── reports.html            # Reports page
│   ├── visualizations.html     # Visualizations page
│   └── 404.html                # Error page
├── static/                   # Static assets for web app
│   ├── css/
│   │   └── style.css           # Main stylesheet
│   └── js/
│       ├── main.js             # Common JavaScript utilities
│       ├── dashboard.js        # Dashboard functionality
│       ├── transactions.js     # Transactions page logic
│       ├── reports.js          # Reports page logic
│       └── visualizations.js   # Visualizations page logic
├── data/                     # Transaction data (created automatically)
├── exports/                  # CSV exports (created automatically)
└── visualizations/           # Generated charts (created automatically)
```

## Example Workflow

### Web Application
1. **Start the web app**: `python app.py`
2. **Open browser**: Navigate to `http://localhost:5000`
3. **View dashboard**: See your financial overview with interactive charts
4. **Add transactions**: Click "Add Income" or "Add Expense" on the dashboard
5. **Manage transactions**: Go to Transactions page to view, filter, and delete
6. **View reports**: Navigate to Reports for monthly/yearly summaries
7. **Explore visualizations**: Check the Visualizations page for interactive charts
8. **Export data**: Download your data as CSV from the Transactions page

### CLI Application
1. **Start the application**: `python main.py`
2. **Add an income transaction**: Choose option 1, select "Income", choose "Salary", enter amount
3. **Add expense transactions**: Choose option 1, select "Expense", choose category, enter amount
4. **View your balance**: Choose option 5
5. **Generate a monthly report**: Choose option 6
6. **Create visualizations**: Choose option 10
7. **Export to CSV**: Choose option 9
8. **Exit and save**: Choose option 0

## Performance

- Apache Spark enables efficient processing of large transaction datasets
- Parquet format provides optimized storage and fast query performance
- Supports thousands of transactions without performance degradation

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open source and available under the MIT License.

## Troubleshooting

### Java Version Issues

If you encounter Java compatibility errors (especially with Java 23), the application includes compatibility fixes. However, for best results:

**Recommended:** Use Java 17 LTS
```bash
# Check your Java version
java -version

# macOS: Install Java 17
brew install openjdk@17
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
```

See the complete [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide for:
- Java version compatibility
- PySpark installation issues
- Memory configuration
- Platform-specific problems
- Common runtime errors

## Support

For issues, questions, or suggestions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first
2. Open an issue on the repository with your environment details
