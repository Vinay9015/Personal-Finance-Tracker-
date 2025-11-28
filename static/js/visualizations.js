// Visualizations Page JavaScript

let charts = {};

// Initialize page
document.addEventListener('DOMContentLoaded', async function() {
    generateYearOptions('trend-year-select');
    await loadAllVisualizations();
});

// Load all visualizations
async function loadAllVisualizations() {
    await Promise.all([
        loadIncomeExpenseChart(),
        loadExpensePieChart(),
        loadMonthlyTrend(),
        loadTopCategoriesChart(),
        loadBalanceOverview()
    ]);
}

// Load income vs expense chart
async function loadIncomeExpenseChart() {
    try {
        const stats = await apiRequest('/api/dashboard/stats');

        const ctx = document.getElementById('incomeExpenseChart').getContext('2d');

        if (charts.incomeExpense) {
            charts.incomeExpense.destroy();
        }

        charts.incomeExpense = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Income', 'Expenses', 'Net Savings'],
                datasets: [{
                    label: 'Amount',
                    data: [stats.total_income, stats.total_expenses, stats.balance],
                    backgroundColor: [
                        'rgba(46, 204, 113, 0.7)',
                        'rgba(231, 76, 60, 0.7)',
                        stats.balance >= 0 ? 'rgba(52, 152, 219, 0.7)' : 'rgba(231, 76, 60, 0.7)'
                    ],
                    borderColor: [
                        '#2ecc71',
                        '#e74c3c',
                        stats.balance >= 0 ? '#3498db' : '#e74c3c'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.parsed.y);
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
    } catch (error) {
        console.error('Error loading income/expense chart:', error);
    }
}

// Load expense pie chart
async function loadExpensePieChart() {
    try {
        const breakdown = await apiRequest('/api/dashboard/category-breakdown');

        if (breakdown.length === 0) {
            document.getElementById('expensePieChart').parentElement.innerHTML =
                '<p class="text-center">No expense data available</p>';
            return;
        }

        const ctx = document.getElementById('expensePieChart').getContext('2d');

        if (charts.expensePie) {
            charts.expensePie.destroy();
        }

        charts.expensePie = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: breakdown.map(item => item.category),
                datasets: [{
                    data: breakdown.map(item => item.total),
                    backgroundColor: [
                        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6',
                        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return context.label + ': ' + formatCurrency(context.parsed) + ' (' + percentage + '%)';
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading expense pie chart:', error);
    }
}

// Load monthly trend
async function loadMonthlyTrend() {
    const year = document.getElementById('trend-year-select').value || new Date().getFullYear();

    try {
        const report = await apiRequest(`/api/reports/yearly?year=${year}`);

        if (!report.monthly_data || report.monthly_data.length === 0) {
            document.getElementById('monthlyTrendChart').parentElement.innerHTML =
                '<p class="text-center">No data available for this year</p>';
            return;
        }

        const ctx = document.getElementById('monthlyTrendChart').getContext('2d');

        if (charts.monthlyTrend) {
            charts.monthlyTrend.destroy();
        }

        charts.monthlyTrend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: report.monthly_data.map(m => m.month_name),
                datasets: [
                    {
                        label: 'Income',
                        data: report.monthly_data.map(m => m.income),
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Expenses',
                        data: report.monthly_data.map(m => m.expenses),
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
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
    } catch (error) {
        console.error('Error loading monthly trend:', error);
    }
}

// Load top categories chart
async function loadTopCategoriesChart() {
    try {
        const breakdown = await apiRequest('/api/dashboard/category-breakdown');

        if (breakdown.length === 0) {
            document.getElementById('topCategoriesChart').parentElement.innerHTML =
                '<p class="text-center">No expense data available</p>';
            return;
        }

        // Get top 5 categories
        const topCategories = breakdown.slice(0, 5);

        const ctx = document.getElementById('topCategoriesChart').getContext('2d');

        if (charts.topCategories) {
            charts.topCategories.destroy();
        }

        charts.topCategories = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topCategories.map(item => item.category),
                datasets: [{
                    label: 'Amount Spent',
                    data: topCategories.map(item => item.total),
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: '#e74c3c',
                    borderWidth: 2
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return formatCurrency(context.parsed.x);
                            }
                        }
                    }
                },
                scales: {
                    x: {
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
    } catch (error) {
        console.error('Error loading top categories chart:', error);
    }
}

// Load balance overview
async function loadBalanceOverview() {
    try {
        const stats = await apiRequest('/api/dashboard/stats');

        document.getElementById('viz-income').textContent = formatCurrency(stats.total_income);
        document.getElementById('viz-expense').textContent = formatCurrency(stats.total_expenses);
        document.getElementById('viz-balance').textContent = formatCurrency(stats.balance);

        const savingsRate = stats.total_income > 0 ?
            ((stats.balance / stats.total_income) * 100).toFixed(1) : 0;
        document.getElementById('viz-savings-rate').textContent = savingsRate + '%';

        // Update balance color
        const balanceElement = document.getElementById('viz-balance');
        balanceElement.style.color = stats.balance >= 0 ? '#2ecc71' : '#e74c3c';

        const savingsElement = document.getElementById('viz-savings-rate');
        savingsElement.style.color = savingsRate >= 0 ? '#2ecc71' : '#e74c3c';
    } catch (error) {
        console.error('Error loading balance overview:', error);
    }
}
