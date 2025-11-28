// Reports Page JavaScript

let yearlyTrendChart = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Populate year selects
    generateYearOptions('year-select');
    generateYearOptions('yearly-select');

    // Set current month
    setCurrentMonth('month-select');

    // Load current month report
    setTimeout(() => loadMonthlyReport(), 100);
});

// Show report section
function showReport(type) {
    // Hide all reports
    document.getElementById('monthly-report').style.display = 'none';
    document.getElementById('yearly-report').style.display = 'none';

    // Show selected report
    document.getElementById(`${type}-report`).style.display = 'block';

    // Update active button
    document.querySelectorAll('.report-selector .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Load report if yearly
    if (type === 'yearly') {
        loadYearlyReport();
    }
}

// Load monthly report
async function loadMonthlyReport() {
    const year = document.getElementById('year-select').value;
    const month = document.getElementById('month-select').value;

    const container = document.getElementById('monthly-report-content');
    container.innerHTML = '<p class="loading">Loading report...</p>';

    try {
        const report = await apiRequest(`/api/reports/monthly?year=${year}&month=${month}`);

        const monthName = new Date(year, month - 1).toLocaleString('en-US', { month: 'long', year: 'numeric' });

        let html = `
            <div class="summary-grid">
                <div class="summary-item">
                    <h4>Total Income</h4>
                    <p style="color: #2ecc71">${formatCurrency(report.total_income)}</p>
                </div>
                <div class="summary-item">
                    <h4>Total Expenses</h4>
                    <p style="color: #e74c3c">${formatCurrency(report.total_expenses)}</p>
                </div>
                <div class="summary-item">
                    <h4>Net Savings</h4>
                    <p style="color: ${report.net_savings >= 0 ? '#2ecc71' : '#e74c3c'}">
                        ${formatCurrency(report.net_savings)}
                    </p>
                </div>
                <div class="summary-item">
                    <h4>Savings Rate</h4>
                    <p>${report.total_income > 0 ? ((report.net_savings / report.total_income) * 100).toFixed(1) : 0}%</p>
                </div>
            </div>
        `;

        // Expense categories
        if (report.expense_categories.length > 0) {
            html += '<h3 style="margin: 2rem 0 1rem;">Expenses by Category</h3>';
            html += '<div class="table-responsive"><table class="table"><thead><tr><th>Category</th><th>Amount</th><th>% of Total</th><th>Transactions</th></tr></thead><tbody>';

            report.expense_categories.forEach(cat => {
                const percentage = (cat.total / report.total_expenses) * 100;
                html += `
                    <tr>
                        <td>${cat.category}</td>
                        <td>${formatCurrency(cat.total)}</td>
                        <td>${percentage.toFixed(1)}%</td>
                        <td>${cat.count}</td>
                    </tr>
                `;
            });

            html += '</tbody></table></div>';
        }

        // Income categories
        if (report.income_categories.length > 0) {
            html += '<h3 style="margin: 2rem 0 1rem;">Income by Category</h3>';
            html += '<div class="table-responsive"><table class="table"><thead><tr><th>Category</th><th>Amount</th><th>% of Total</th><th>Transactions</th></tr></thead><tbody>';

            report.income_categories.forEach(cat => {
                const percentage = (cat.total / report.total_income) * 100;
                html += `
                    <tr>
                        <td>${cat.category}</td>
                        <td>${formatCurrency(cat.total)}</td>
                        <td>${percentage.toFixed(1)}%</td>
                        <td>${cat.count}</td>
                    </tr>
                `;
            });

            html += '</tbody></table></div>';
        }

        container.innerHTML = html;
    } catch (error) {
        container.innerHTML = '<p class="text-center text-warning">No data available for this period</p>';
    }
}

// Load yearly report
async function loadYearlyReport() {
    const year = document.getElementById('yearly-select').value;

    const container = document.getElementById('yearly-report-content');
    container.innerHTML = '<p class="loading">Loading report...</p>';

    try {
        const report = await apiRequest(`/api/reports/yearly?year=${year}`);

        if (!report.monthly_data || report.monthly_data.length === 0) {
            container.innerHTML = '<p class="text-center">No data available for this year</p>';
            return;
        }

        // Calculate totals
        const totalIncome = report.monthly_data.reduce((sum, m) => sum + m.income, 0);
        const totalExpenses = report.monthly_data.reduce((sum, m) => sum + m.expenses, 0);
        const netSavings = totalIncome - totalExpenses;

        let html = `
            <div class="summary-grid">
                <div class="summary-item">
                    <h4>Total Income</h4>
                    <p style="color: #2ecc71">${formatCurrency(totalIncome)}</p>
                </div>
                <div class="summary-item">
                    <h4>Total Expenses</h4>
                    <p style="color: #e74c3c">${formatCurrency(totalExpenses)}</p>
                </div>
                <div class="summary-item">
                    <h4>Net Savings</h4>
                    <p style="color: ${netSavings >= 0 ? '#2ecc71' : '#e74c3c'}">
                        ${formatCurrency(netSavings)}
                    </p>
                </div>
                <div class="summary-item">
                    <h4>Savings Rate</h4>
                    <p>${totalIncome > 0 ? ((netSavings / totalIncome) * 100).toFixed(1) : 0}%</p>
                </div>
            </div>

            <h3 style="margin: 2rem 0 1rem;">Monthly Breakdown</h3>
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Income</th>
                            <th>Expenses</th>
                            <th>Savings</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        report.monthly_data.forEach(month => {
            html += `
                <tr>
                    <td>${month.month_name}</td>
                    <td style="color: #2ecc71">${formatCurrency(month.income)}</td>
                    <td style="color: #e74c3c">${formatCurrency(month.expenses)}</td>
                    <td style="color: ${month.savings >= 0 ? '#2ecc71' : '#e74c3c'}">
                        ${formatCurrency(month.savings)}
                    </td>
                </tr>
            `;
        });

        html += '</tbody></table></div>';

        container.innerHTML = html;

        // Update chart
        updateYearlyTrendChart(report.monthly_data);
    } catch (error) {
        container.innerHTML = '<p class="text-center text-warning">No data available for this year</p>';
    }
}

// Update yearly trend chart
function updateYearlyTrendChart(monthlyData) {
    const ctx = document.getElementById('yearlyTrendChart').getContext('2d');

    const labels = monthlyData.map(m => m.month_name);
    const incomeData = monthlyData.map(m => m.income);
    const expenseData = monthlyData.map(m => m.expenses);

    if (yearlyTrendChart) {
        yearlyTrendChart.destroy();
    }

    yearlyTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Income',
                    data: incomeData,
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Expenses',
                    data: expenseData,
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}
