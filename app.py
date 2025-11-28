#!/usr/bin/env python3
"""
Personal Finance Tracker - Web Application
Flask-based web interface with Apache Spark backend
"""

from flask import Flask, render_template, request, jsonify, send_file
from datetime import datetime
import sys
import os
import io
import base64

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from spark_backend import SparkBackend
from transaction_manager import TransactionManager
from report_generator import ReportGenerator
from csv_exporter import CSVExporter
from visualizer import DataVisualizer

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize backend components (singleton pattern)
backend = None
transaction_manager = None
report_generator = None
csv_exporter = None
visualizer = None


def init_backend():
    """Initialize backend components"""
    global backend, transaction_manager, report_generator, csv_exporter, visualizer

    if backend is None:
        print("Initializing Apache Spark backend...")
        backend = SparkBackend(data_path="data/transactions")
        backend.load_data()

        transaction_manager = TransactionManager(backend)
        report_generator = ReportGenerator(backend)
        csv_exporter = CSVExporter(backend)
        visualizer = DataVisualizer(backend)
        print("Backend initialized successfully!")


# Initialize backend on startup
init_backend()


# ============================================================================
# WEB ROUTES
# ============================================================================

@app.route('/')
def index():
    """Dashboard homepage"""
    return render_template('index.html')


@app.route('/transactions')
def transactions_page():
    """Transactions management page"""
    return render_template('transactions.html')


@app.route('/reports')
def reports_page():
    """Reports and analytics page"""
    return render_template('reports.html')


@app.route('/visualizations')
def visualizations_page():
    """Data visualizations page"""
    return render_template('visualizations.html')


# ============================================================================
# API ENDPOINTS - Dashboard
# ============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        df = backend.get_all_transactions()

        if df is None or df.count() == 0:
            return jsonify({
                'total_income': 0,
                'total_expenses': 0,
                'balance': 0,
                'transaction_count': 0
            })

        from pyspark.sql import functions as F

        # Calculate totals
        income_df = df.filter(df.type == "income")
        expense_df = df.filter(df.type == "expense")

        total_income = income_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        total_expenses = expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        balance = total_income - total_expenses

        return jsonify({
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'balance': float(balance),
            'transaction_count': df.count()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/recent-transactions', methods=['GET'])
def get_recent_transactions():
    """Get recent transactions for dashboard"""
    try:
        df = backend.get_all_transactions()

        if df is None or df.count() == 0:
            return jsonify([])

        # Get last 10 transactions
        recent = df.orderBy("created_at", ascending=False).limit(10).toPandas()

        transactions = []
        for _, row in recent.iterrows():
            transactions.append({
                'id': row['transaction_id'],
                'date': row['date'],
                'type': row['type'],
                'category': row['category'],
                'amount': float(row['amount']),
                'description': row['description'] or ''
            })

        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/category-breakdown', methods=['GET'])
def get_category_breakdown():
    """Get expense breakdown by category"""
    try:
        from pyspark.sql import functions as F

        expense_df = backend.filter_by_type("expense")

        if expense_df is None or expense_df.count() == 0:
            return jsonify([])

        category_totals = expense_df.groupBy("category").agg(
            F.sum("amount").alias("total")
        ).orderBy("total", ascending=False).collect()

        breakdown = []
        for row in category_totals:
            breakdown.append({
                'category': row.category,
                'total': float(row.total)
            })

        return jsonify(breakdown)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - Transactions
# ============================================================================

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional filters"""
    try:
        transaction_type = request.args.get('type')
        category = request.args.get('category')
        limit = request.args.get('limit', type=int)

        df = backend.get_all_transactions()

        if df is None or df.count() == 0:
            return jsonify([])

        # Apply filters
        if transaction_type:
            df = df.filter(df.type == transaction_type)
        if category:
            df = df.filter(df.category == category)

        # Convert to pandas and sort
        transactions_df = df.orderBy("date", ascending=False).toPandas()

        if limit:
            transactions_df = transactions_df.head(limit)

        transactions = []
        for _, row in transactions_df.iterrows():
            transactions.append({
                'id': row['transaction_id'],
                'date': row['date'],
                'type': row['type'],
                'category': row['category'],
                'amount': float(row['amount']),
                'description': row['description'] or '',
                'created_at': row['created_at']
            })

        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add a new transaction"""
    try:
        data = request.json

        success = transaction_manager.add_transaction(
            transaction_type=data['type'],
            category=data['category'],
            amount=float(data['amount']),
            description=data.get('description', ''),
            date=data.get('date')
        )

        if success:
            backend.save_data()
            return jsonify({'success': True, 'message': 'Transaction added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add transaction'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transactions/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        success = transaction_manager.remove_transaction(transaction_id)

        if success:
            backend.save_data()
            return jsonify({'success': True, 'message': 'Transaction deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Transaction not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get available categories"""
    return jsonify({
        'income': transaction_manager.INCOME_CATEGORIES,
        'expense': transaction_manager.EXPENSE_CATEGORIES
    })


# ============================================================================
# API ENDPOINTS - Reports
# ============================================================================

@app.route('/api/reports/monthly', methods=['GET'])
def get_monthly_report():
    """Get monthly report data"""
    try:
        year = request.args.get('year', type=int) or datetime.now().year
        month = request.args.get('month', type=int) or datetime.now().month

        # Create date range
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        df = backend.filter_by_date_range(start_date, end_date)

        if df.count() == 0:
            return jsonify({'error': 'No data for this period'}), 404

        from pyspark.sql import functions as F

        # Calculate totals
        income_df = df.filter(df.type == "income")
        expense_df = df.filter(df.type == "expense")

        total_income = income_df.agg(F.sum("amount")).collect()[0][0] or 0.0
        total_expenses = expense_df.agg(F.sum("amount")).collect()[0][0] or 0.0

        # Category breakdown
        expense_categories = expense_df.groupBy("category").agg(
            F.sum("amount").alias("total"),
            F.count("*").alias("count")
        ).orderBy("total", ascending=False).collect()

        income_categories = income_df.groupBy("category").agg(
            F.sum("amount").alias("total"),
            F.count("*").alias("count")
        ).orderBy("total", ascending=False).collect()

        return jsonify({
            'year': year,
            'month': month,
            'total_income': float(total_income),
            'total_expenses': float(total_expenses),
            'net_savings': float(total_income - total_expenses),
            'expense_categories': [{'category': r.category, 'total': float(r.total), 'count': r.count} for r in expense_categories],
            'income_categories': [{'category': r.category, 'total': float(r.total), 'count': r.count} for r in income_categories]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/yearly', methods=['GET'])
def get_yearly_report():
    """Get yearly report data"""
    try:
        year = request.args.get('year', type=int) or datetime.now().year

        monthly_data = []
        for month in range(1, 13):
            month_start = f"{year}-{month:02d}-01"
            if month == 12:
                month_end = f"{year + 1}-01-01"
            else:
                month_end = f"{year}-{month + 1:02d}-01"

            month_df = backend.filter_by_date_range(month_start, month_end)

            if month_df.count() > 0:
                from pyspark.sql import functions as F

                income = month_df.filter(month_df.type == "income").agg(F.sum("amount")).collect()[0][0] or 0.0
                expenses = month_df.filter(month_df.type == "expense").agg(F.sum("amount")).collect()[0][0] or 0.0

                monthly_data.append({
                    'month': month,
                    'month_name': datetime(year, month, 1).strftime("%B"),
                    'income': float(income),
                    'expenses': float(expenses),
                    'savings': float(income - expenses)
                })

        return jsonify({
            'year': year,
            'monthly_data': monthly_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# API ENDPOINTS - Export
# ============================================================================

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export transactions to CSV"""
    try:
        export_type = request.args.get('type', 'all')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transactions_{export_type}_{timestamp}.csv"

        if export_type == 'all':
            csv_exporter.export_all_transactions(f"exports/{filename}")
        elif export_type == 'income':
            csv_exporter.export_by_type('income', f"exports/{filename}")
        elif export_type == 'expense':
            csv_exporter.export_by_type('expense', f"exports/{filename}")

        return send_file(f"exports/{filename}", as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# CLEANUP
# ============================================================================

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Save data on app shutdown"""
    if backend is not None:
        backend.save_data()


if __name__ == '__main__':
    print("=" * 70)
    print("  PERSONAL FINANCE TRACKER - WEB APPLICATION")
    print("  Powered by Flask + Apache Spark")
    print("=" * 70)
    print("\nStarting web server...")
    print("Access the application at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")

    try:
        app.run(debug=True, host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        if backend:
            backend.save_data()
            backend.stop()
        print("Server stopped. Data saved successfully.")
