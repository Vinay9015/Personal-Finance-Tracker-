// Dashboard JavaScript

let categoryChart = null;
let categories = {};

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', async function() {
    await loadCategories();
    await loadDashboardStats();
    await loadRecentTransactions();
    await loadCategoryBreakdown();

    // Set today's date in add transaction form
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.value = getTodayDate();
    }
});

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const stats = await apiRequest('/api/dashboard/stats');

        document.getElementById('total-income').textContent = formatCurrency(stats.total_income);
        document.getElementById('total-expenses').textContent = formatCurrency(stats.total_expenses);
        document.getElementById('balance').textContent = formatCurrency(stats.balance);
        document.getElementById('transaction-count').textContent = stats.transaction_count;

        // Update balance color
        const balanceElement = document.getElementById('balance');
        if (stats.balance >= 0) {
            balanceElement.style.color = '#2ecc71';
        } else {
            balanceElement.style.color = '#e74c3c';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load recent transactions
async function loadRecentTransactions() {
    try {
        const transactions = await apiRequest('/api/dashboard/recent-transactions');

        const container = document.getElementById('recent-transactions');

        if (transactions.length === 0) {
            container.innerHTML = '<p class="text-center">No transactions yet</p>';
            return;
        }

        let html = '<div class="transaction-list">';
        transactions.forEach(trans => {
            const typeClass = trans.type === 'income' ? 'income' : 'expense';
            const icon = trans.type === 'income' ? 'fa-arrow-up' : 'fa-arrow-down';

            html += `
                <div class="transaction-item">
                    <div class="transaction-icon ${typeClass}">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="transaction-details">
                        <div class="transaction-category">${trans.category}</div>
                        <div class="transaction-date">${formatDate(trans.date)}</div>
                    </div>
                    <div class="transaction-amount ${typeClass}">
                        ${trans.type === 'income' ? '+' : '-'}${formatCurrency(trans.amount)}
                    </div>
                </div>
            `;
        });
        html += '</div>';

        container.innerHTML = html;

        // Add CSS for transaction list
        addTransactionListStyles();
    } catch (error) {
        console.error('Error loading recent transactions:', error);
    }
}

// Load category breakdown chart
async function loadCategoryBreakdown() {
    try {
        const breakdown = await apiRequest('/api/dashboard/category-breakdown');

        if (breakdown.length === 0) {
            const canvas = document.getElementById('categoryChart');
            canvas.parentElement.innerHTML = '<p class="text-center">No expense data available</p>';
            return;
        }

        const labels = breakdown.map(item => item.category);
        const data = breakdown.map(item => item.total);

        const ctx = document.getElementById('categoryChart').getContext('2d');

        if (categoryChart) {
            categoryChart.destroy();
        }

        categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
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
                                return context.label + ': ' + formatCurrency(context.parsed);
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading category breakdown:', error);
    }
}

// Load categories
async function loadCategories() {
    try {
        categories = await apiRequest('/api/categories');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Show add transaction modal
function showAddTransactionModal(type) {
    const modal = document.getElementById('addTransactionModal');
    const modalTitle = document.getElementById('modal-title');
    const typeInput = document.getElementById('transaction-type');
    const categorySelect = document.getElementById('category');

    // Set title and type
    modalTitle.textContent = `Add ${type.charAt(0).toUpperCase() + type.slice(1)}`;
    typeInput.value = type;

    // Populate categories
    categorySelect.innerHTML = '<option value="">Select category...</option>';
    const categoryList = type === 'income' ? categories.income : categories.expense;

    categoryList.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categorySelect.appendChild(option);
    });

    // Show modal
    modal.classList.add('show');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('addTransactionModal');
    modal.classList.remove('show');
    document.getElementById('addTransactionForm').reset();
}

// Add transaction
async function addTransaction(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    const data = {
        type: formData.get('type'),
        category: formData.get('category'),
        amount: parseFloat(formData.get('amount')),
        description: formData.get('description'),
        date: formData.get('date')
    };

    try {
        await apiRequest('/api/transactions', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showNotification('Transaction added successfully!');
        closeModal();

        // Reload dashboard data
        await loadDashboardStats();
        await loadRecentTransactions();
        await loadCategoryBreakdown();
    } catch (error) {
        console.error('Error adding transaction:', error);
    }
}

// Add custom styles for transaction list
function addTransactionListStyles() {
    if (document.getElementById('transaction-list-styles')) return;

    const style = document.createElement('style');
    style.id = 'transaction-list-styles';
    style.textContent = `
        .transaction-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }

        .transaction-item {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.75rem;
            background-color: #f8f9fa;
            border-radius: 4px;
            transition: background-color 0.3s;
        }

        .transaction-item:hover {
            background-color: #e9ecef;
        }

        .transaction-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .transaction-icon.income {
            background-color: rgba(46, 204, 113, 0.1);
            color: #2ecc71;
        }

        .transaction-icon.expense {
            background-color: rgba(231, 76, 60, 0.1);
            color: #e74c3c;
        }

        .transaction-details {
            flex: 1;
        }

        .transaction-category {
            font-weight: 500;
            color: #2c3e50;
        }

        .transaction-date {
            font-size: 0.875rem;
            color: #7f8c8d;
        }

        .transaction-amount {
            font-weight: 600;
            font-size: 1.125rem;
        }

        .transaction-amount.income {
            color: #2ecc71;
        }

        .transaction-amount.expense {
            color: #e74c3c;
        }
    `;
    document.head.appendChild(style);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('addTransactionModal');
    if (event.target === modal) {
        closeModal();
    }
}
