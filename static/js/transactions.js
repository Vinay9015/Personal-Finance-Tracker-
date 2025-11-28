// Transactions Page JavaScript

let allTransactions = [];
let categories = {};
let deleteTransactionId = null;

// Load data on page load
document.addEventListener('DOMContentLoaded', async function() {
    await loadCategories();
    await loadTransactions();
    populateCategoryFilter();

    // Set today's date
    const dateInput = document.getElementById('trans-date');
    if (dateInput) {
        dateInput.value = getTodayDate();
    }
});

// Load categories
async function loadCategories() {
    try {
        categories = await apiRequest('/api/categories');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

// Load all transactions
async function loadTransactions(filterType = '', filterCategory = '') {
    try {
        let url = '/api/transactions?';
        if (filterType) url += `type=${filterType}&`;
        if (filterCategory) url += `category=${filterCategory}&`;

        allTransactions = await apiRequest(url);
        displayTransactions(allTransactions);
    } catch (error) {
        console.error('Error loading transactions:', error);
    }
}

// Display transactions in table
function displayTransactions(transactions) {
    const tbody = document.getElementById('transactions-body');

    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No transactions found</td></tr>';
        return;
    }

    let html = '';
    transactions.forEach(trans => {
        const badgeClass = trans.type === 'income' ? 'badge-income' : 'badge-expense';

        html += `
            <tr>
                <td>${formatDate(trans.date)}</td>
                <td><span class="badge ${badgeClass}">${trans.type}</span></td>
                <td>${trans.category}</td>
                <td>${formatCurrency(trans.amount)}</td>
                <td>${trans.description || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-danger" onclick="showDeleteModal('${trans.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Populate category filter
function populateCategoryFilter() {
    const select = document.getElementById('filter-category');

    // Combine all categories
    const allCategories = [...categories.income, ...categories.expense].sort();
    const uniqueCategories = [...new Set(allCategories)];

    uniqueCategories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        select.appendChild(option);
    });
}

// Filter transactions
function filterTransactions() {
    const filterType = document.getElementById('filter-type').value;
    const filterCategory = document.getElementById('filter-category').value;

    loadTransactions(filterType, filterCategory);
}

// Clear filters
function clearFilters() {
    document.getElementById('filter-type').value = '';
    document.getElementById('filter-category').value = '';
    loadTransactions();
}

// Show add transaction modal
function showAddTransactionModal() {
    const modal = document.getElementById('transactionModal');
    const form = document.getElementById('transactionForm');

    form.reset();
    document.getElementById('modal-title').textContent = 'Add Transaction';
    document.getElementById('trans-date').value = getTodayDate();

    modal.classList.add('show');
}

// Close transaction modal
function closeTransactionModal() {
    const modal = document.getElementById('transactionModal');
    modal.classList.remove('show');
}

// Update category options based on type
function updateCategoryOptions() {
    const type = document.getElementById('trans-type').value;
    const categorySelect = document.getElementById('trans-category');

    categorySelect.innerHTML = '<option value="">Select category...</option>';

    if (!type) return;

    const categoryList = type === 'income' ? categories.income : categories.expense;

    categoryList.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categorySelect.appendChild(option);
    });
}

// Submit transaction
async function submitTransaction(event) {
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
        closeTransactionModal();
        await loadTransactions();
    } catch (error) {
        console.error('Error adding transaction:', error);
    }
}

// Show delete modal
function showDeleteModal(transactionId) {
    deleteTransactionId = transactionId;
    const modal = document.getElementById('deleteModal');
    modal.classList.add('show');
}

// Close delete modal
function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    modal.classList.remove('show');
    deleteTransactionId = null;
}

// Confirm delete
async function confirmDelete() {
    if (!deleteTransactionId) return;

    try {
        await apiRequest(`/api/transactions/${deleteTransactionId}`, {
            method: 'DELETE'
        });

        showNotification('Transaction deleted successfully!');
        closeDeleteModal();
        await loadTransactions();
    } catch (error) {
        console.error('Error deleting transaction:', error);
    }
}

// Export to CSV
function exportCSV(type) {
    window.location.href = `/api/export/csv?type=${type}`;
    showNotification(`Exporting ${type} transactions...`);
}

// Close modals when clicking outside
window.onclick = function(event) {
    const transModal = document.getElementById('transactionModal');
    const delModal = document.getElementById('deleteModal');

    if (event.target === transModal) {
        closeTransactionModal();
    }
    if (event.target === delModal) {
        closeDeleteModal();
    }
}
