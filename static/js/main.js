// Utility: Format currency to Rupiah (e.g., Rp 9.341.000)
function formatRupiah(value) {
    const isNegative = value < 0;
    const absVal = Math.abs(value);
    const formatted = new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(absVal);
    
    // Replace standard 'Rp' formatting space
    const cleanFormatted = formatted.replace("Rp", "Rp ").trim();
    return isNegative ? `- ${cleanFormatted}` : cleanFormatted;
}

// Utility: Format Date (e.g., "27 Jun")
function formatDateLabel(dateString) {
    if (!dateString) return '';
    const dateObj = new Date(dateString);
    const day = dateObj.getDate();
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'];
    const month = months[dateObj.getMonth()];
    return `${day} ${month}`;
}

// Handle Login Form
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const alertEl = document.getElementById('alert-msg');
        
        alertEl.style.display = 'none';
        
        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            if (response.ok && data.success) {
                alertEl.className = 'alert alert-success';
                alertEl.textContent = data.message;
                alertEl.style.display = 'block';
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 800);
            } else {
                alertEl.className = 'alert alert-error';
                alertEl.textContent = data.message || 'Login gagal.';
                alertEl.style.display = 'block';
            }
        } catch (err) {
            alertEl.className = 'alert alert-error';
            alertEl.textContent = 'Terjadi kesalahan koneksi server.';
            alertEl.style.display = 'block';
        }
    });
}

// Handle Register Form
const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const alertEl = document.getElementById('alert-msg');
        
        alertEl.style.display = 'none';
        
        if (password !== confirmPassword) {
            alertEl.className = 'alert alert-error';
            alertEl.textContent = 'Konfirmasi kata sandi tidak cocok!';
            alertEl.style.display = 'block';
            return;
        }
        
        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });
            
            const data = await response.json();
            if (response.ok && data.success) {
                alertEl.className = 'alert alert-success';
                alertEl.textContent = data.message;
                alertEl.style.display = 'block';
                setTimeout(() => {
                    window.location.href = '/login';
                }, 1500);
            } else {
                alertEl.className = 'alert alert-error';
                alertEl.textContent = data.message || 'Registrasi gagal.';
                alertEl.style.display = 'block';
            }
        } catch (err) {
            alertEl.className = 'alert alert-error';
            alertEl.textContent = 'Terjadi kesalahan koneksi server.';
            alertEl.style.display = 'block';
        }
    });
}

// ==========================================
// LOGIKA DASHBOARD
// ==========================================
const dashboardContent = document.getElementById('dashboard-page');
if (dashboardContent) {
    let currentFilterType = 'all'; // all, income, expense
    let currentSearchQuery = '';
    
    // Inisialisasi bulan default sesuai date hari ini (misal Juni 2026)
    const today = new Date();
    let selectedYear = today.getFullYear();
    let selectedMonth = today.getMonth() + 1; // 1-indexed

    // DOM Elements
    const monthSelect = document.getElementById('month-select');
    const searchInput = document.getElementById('search-input');
    const filterTabs = document.querySelectorAll('.filter-tab');
    const transactionContainer = document.getElementById('transactions-container');
    const categoryBreakdownContainer = document.getElementById('category-breakdown');
    
    // Metrics DOM
    const totalSaldoVal = document.getElementById('total-saldo-value');
    const totalSaldoCount = document.getElementById('total-saldo-count');
    const monthlyIncomeVal = document.getElementById('monthly-income-value');
    const monthlyIncomeLabel = document.getElementById('monthly-income-label');
    const monthlyExpenseVal = document.getElementById('monthly-expense-value');
    const monthlyExpenseLabel = document.getElementById('monthly-expense-label');
    const breakdownLabel = document.getElementById('breakdown-label');
    
    // Modal DOM
    const transactionModal = document.getElementById('transaction-modal');
    const modalTitle = document.getElementById('modal-title');
    const transactionForm = document.getElementById('transaction-form');
    const modalTxId = document.getElementById('modal-tx-id');
    const modalCategory = document.getElementById('modal-category');
    const modalAmount = document.getElementById('modal-amount');
    const modalNote = document.getElementById('modal-note');
    const modalDate = document.getElementById('modal-date');
    const btnCancelModal = document.getElementById('btn-cancel-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnAddTx = document.getElementById('btn-add-tx');
    const btnLogout = document.getElementById('btn-logout');

    // Populate Month Picker Dropdown (12 bulan sebelum, 6 bulan sesudah)
    function populateMonthPicker() {
        monthSelect.innerHTML = '';
        const monthNames = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ];
        
        // Buat rentang dari Jan 2025 hingga Des 2027 agar mencakup 2026 di screenshot
        const startYear = 2025;
        const endYear = 2027;
        
        for (let y = startYear; y <= endYear; y++) {
            for (let m = 1; m <= 12; m++) {
                const opt = document.createElement('option');
                opt.value = `${y}-${m}`;
                opt.textContent = `${monthNames[m-1]} ${y}`;
                
                if (y === selectedYear && m === selectedMonth) {
                    opt.selected = true;
                }
                monthSelect.appendChild(opt);
            }
        }
    }

    // Mengambil Nama Bulan
    function getMonthName(m) {
        const monthNames = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ];
        return monthNames[m - 1];
    }

    // Refresh data ringkasan widget dashboard
    async function loadSummary() {
        try {
            const res = await fetch(`/api/summary?year=${selectedYear}&month=${selectedMonth}`);
            if (!res.ok) return;
            const data = await res.json();
            
            // Format labels
            const monthYearLabel = `${getMonthName(selectedMonth)} ${selectedYear}`;
            monthlyIncomeLabel.textContent = `Pemasukan • ${monthYearLabel}`;
            monthlyExpenseLabel.textContent = `Pengeluaran • ${monthYearLabel}`;
            breakdownLabel.textContent = `Per kategori • ${monthYearLabel}`;
            
            // Set values
            totalSaldoVal.textContent = formatRupiah(data.total_saldo);
            totalSaldoCount.textContent = `${data.total_transactions_count} transaksi tercatat`;
            
            monthlyIncomeVal.textContent = formatRupiah(data.monthly_income);
            monthlyExpenseVal.textContent = formatRupiah(data.monthly_expense);
            
            // Render category breakdown
            renderCategoryBreakdown(data.category_spending, data.monthly_expense);
        } catch (err) {
            console.error('Error loading summary:', err);
        }
    }

    // Render Progress Bar Pengeluaran per Kategori
    function renderCategoryBreakdown(categories, totalExpense) {
        categoryBreakdownContainer.innerHTML = '';
        if (!categories || categories.length === 0) {
            categoryBreakdownContainer.innerHTML = `
                <div class="empty-state" style="padding: 1rem 0;">
                    <p style="font-size: 0.85rem;">Belum ada pengeluaran di bulan ini.</p>
                </div>
            `;
            return;
        }
        
        categories.forEach(item => {
            const percentage = totalExpense > 0 ? (item.total / totalExpense) * 100 : 0;
            
            const catRow = document.createElement('div');
            catRow.className = 'category-row';
            catRow.innerHTML = `
                <div class="category-row-header">
                    <span class="cat-row-name">${item.category}</span>
                    <span class="cat-row-value">${formatRupiah(item.total)}</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: 0%"></div>
                </div>
            `;
            categoryBreakdownContainer.appendChild(catRow);
            
            // Trigger animation
            setTimeout(() => {
                const fill = catRow.querySelector('.progress-bar-fill');
                if (fill) fill.style.width = `${percentage}%`;
            }, 100);
        });
    }

    // Refresh daftar transaksi
    async function loadTransactions() {
        try {
            const url = `/api/transactions?type=${currentFilterType}&search=${encodeURIComponent(currentSearchQuery)}&year=${selectedYear}&month=${selectedMonth}`;
            const res = await fetch(url);
            if (!res.ok) return;
            const txs = await res.json();
            
            transactionContainer.innerHTML = '';
            
            if (txs.length === 0) {
                transactionContainer.innerHTML = `
                    <div class="empty-state">
                        <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 9h-4v4h-2v-4H7v-2h4V6h2v4h4v2z"/></svg>
                        <p>Tidak ada transaksi yang cocok.</p>
                    </div>
                `;
                return;
            }
            
            txs.forEach(tx => {
                const item = document.createElement('div');
                item.className = 'transaction-item';
                
                const isIncome = tx.type === 'income';
                const sign = isIncome ? '+' : '-';
                const colorClass = isIncome ? 'income' : 'expense';
                const badgeLabel = isIncome ? 'MASUK' : 'KELUAR';
                const badgeClass = isIncome ? 'badge-income' : 'badge-expense';
                
                // SVG icon: green arrow-up-right or red arrow-down-left
                const iconSvg = isIncome 
                    ? `<svg viewBox="0 0 24 24" width="20" height="20"><path d="M5 17.59L15.59 7H9V5h10v10h-2V8.41L6.41 19 5 17.59z"/></svg>`
                    : `<svg viewBox="0 0 24 24" width="20" height="20"><path d="M19 6.41L17.59 5 7 15.59V9H5v10h10v-2H8.41L19 6.41z"/></svg>`;
                
                item.innerHTML = `
                    <div class="tx-left">
                        <div class="tx-icon-wrapper ${colorClass}">
                            ${iconSvg}
                        </div>
                        <div class="tx-details">
                            <div class="tx-category-line">
                                <span class="tx-category">${tx.category}</span>
                                <span class="tx-badge ${badgeClass}">${badgeLabel}</span>
                            </div>
                            <span class="tx-note">${tx.note || '-'}</span>
                        </div>
                    </div>
                    <div class="tx-right">
                        <div class="tx-amount-date">
                            <span class="tx-amount ${colorClass}">${sign} ${formatRupiah(tx.amount)}</span>
                            <span class="tx-date">${formatDateLabel(tx.date)}</span>
                        </div>
                        <div class="tx-actions">
                            <button class="btn-action btn-edit" title="Edit Transaksi" data-id="${tx.id}">
                                <svg viewBox="0 0 24 24"><path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/></svg>
                            </button>
                            <button class="btn-action btn-delete" title="Hapus Transaksi" data-id="${tx.id}">
                                <svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                            </button>
                        </div>
                    </div>
                `;
                
                transactionContainer.appendChild(item);
            });
            
            // Bind actions
            document.querySelectorAll('.btn-edit').forEach(btn => {
                btn.addEventListener('click', () => openEditModal(btn.dataset.id));
            });
            
            document.querySelectorAll('.btn-delete').forEach(btn => {
                btn.addEventListener('click', () => deleteTransaction(btn.dataset.id));
            });
            
        } catch (err) {
            console.error('Error loading transactions:', err);
        }
    }

    // Setup Modal untuk Tambah Transaksi
    function openAddModal() {
        modalTitle.textContent = 'Tambah Transaksi';
        modalTxId.value = '';
        transactionForm.reset();
        
        // Set default radio ke expense
        document.getElementById('radio-expense').checked = true;
        
        // Set default date ke hari ini
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        modalDate.value = `${yyyy}-${mm}-${dd}`;
        
        transactionModal.classList.add('active');
    }

    // Setup Modal untuk Edit Transaksi
    async function openEditModal(id) {
        try {
            // Kita filter dari transaksi lokal untuk mengisi form modal
            const res = await fetch(`/api/transactions?year=${selectedYear}&month=${selectedMonth}`);
            if (!res.ok) return;
            const txs = await res.json();
            const tx = txs.find(t => t.id == id);
            
            if (!tx) return;
            
            modalTitle.textContent = 'Edit Transaksi';
            modalTxId.value = tx.id;
            modalCategory.value = tx.category;
            modalAmount.value = tx.amount;
            modalNote.value = tx.note || '';
            modalDate.value = tx.date;
            
            if (tx.type === 'income') {
                document.getElementById('radio-income').checked = true;
            } else {
                document.getElementById('radio-expense').checked = true;
            }
            
            transactionModal.classList.add('active');
        } catch (err) {
            console.error('Error opening edit modal:', err);
        }
    }

    // Menghapus Transaksi
    async function deleteTransaction(id) {
        if (!confirm('Apakah Anda yakin ingin menghapus transaksi ini?')) return;
        
        try {
            const res = await fetch(`/api/transactions/${id}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                loadDashboard();
            } else {
                alert('Gagal menghapus transaksi.');
            }
        } catch (err) {
            console.error('Error deleting transaction:', err);
        }
    }

    // Simpan data transaksi (Tambah / Edit)
    transactionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const txId = modalTxId.value;
        const type = document.querySelector('input[name="type"]:checked').value;
        const category = modalCategory.value;
        const amount = modalAmount.value;
        const note = modalNote.value;
        const dateVal = modalDate.value;
        
        const payload = { type, category, amount, note, date: dateVal };
        
        const url = txId ? `/api/transactions/${txId}` : '/api/transactions';
        const method = txId ? 'PUT' : 'POST';
        
        try {
            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                // Tutup modal
                transactionModal.classList.remove('active');
                
                // Jika transaksi di luar bulan yang sedang aktif, update bulan aktif
                const txDateObj = new Date(dateVal);
                selectedYear = txDateObj.getFullYear();
                selectedMonth = txDateObj.getMonth() + 1;
                
                // Refresh data
                populateMonthPicker();
                loadDashboard();
            } else {
                const data = await res.json();
                alert(data.message || 'Gagal menyimpan transaksi.');
            }
        } catch (err) {
            console.error('Error saving transaction:', err);
        }
    });

    // Helper load all dashboard components
    function loadDashboard() {
        loadSummary();
        loadTransactions();
    }

    // Event Listeners untuk Dashboard Controls
    monthSelect.addEventListener('change', (e) => {
        const [y, m] = e.target.value.split('-');
        selectedYear = parseInt(y);
        selectedMonth = parseInt(m);
        loadDashboard();
    });

    // Search dengan debouncing sederhana
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentSearchQuery = e.target.value;
            loadTransactions();
        }, 300);
    });

    // Filter Tabs
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentFilterType = tab.dataset.type;
            loadTransactions();
        });
    });

    // Modal Control triggers
    btnAddTx.addEventListener('click', openAddModal);
    btnCloseModal.addEventListener('click', () => transactionModal.classList.remove('active'));
    btnCancelModal.addEventListener('click', () => transactionModal.classList.remove('active'));
    
    // Close modal click outside
    window.addEventListener('click', (e) => {
        if (e.target === transactionModal) {
            transactionModal.classList.remove('active');
        }
    });

    // Logout
    btnLogout.addEventListener('click', async () => {
        try {
            const res = await fetch('/api/logout', { method: 'POST' });
            if (res.ok) {
                window.location.href = '/login';
            }
        } catch (err) {
            console.error('Error during logout:', err);
        }
    });

    // Initialize Dashboard
    populateMonthPicker();
    loadDashboard();
}
