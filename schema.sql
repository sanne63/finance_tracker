-- ==========================================
-- SKEMA DAN QUERY DATABASE MYSQL
-- PERSONAL FINANCE TRACKER
-- ==========================================

-- 1. PEMBUATAN DATABASE & TABEL
CREATE DATABASE IF NOT EXISTS finance_tracker;
USE finance_tracker;

-- Tabel Users untuk penanganan registrasi dan login
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabel Transactions dengan relasi ke tabel Users
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type ENUM('income', 'expense') NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    note TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- REFERENSI QUERY UTAMA YANG DIGUNAKAN DI BACKEND
-- ==========================================

-- [USER MANAGEMENT]
-- A. Registrasi User Baru
-- INSERT INTO users (name, email, password_hash) VALUES (:name, :email, :password_hash);

-- B. Login / Cari User berdasarkan Email
-- SELECT id, name, email, password_hash FROM users WHERE email = :email;


-- [TRANSACTIONS CRUD]
-- A. Menambah Transaksi Baru
-- INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (:user_id, :type, :category, :amount, :note, :date);

-- B. Mengambil Semua Transaksi untuk User Tertentu (Urut Tanggal Terbaru)
-- SELECT id, type, category, amount, note, DATE_FORMAT(date, '%Y-%m-%d') as date 
-- FROM transactions 
-- WHERE user_id = :user_id 
-- ORDER BY date DESC;

-- C. Mengambil Ringkasan Saldo (Total Income & Expense) untuk User
-- SELECT 
--     COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
--     COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense
-- FROM transactions 
-- WHERE user_id = :user_id;

-- D. Mengambil Transaksi Bulanan untuk User
-- SELECT id, type, category, amount, note, DATE_FORMAT(date, '%Y-%m-%d') as date
-- FROM transactions 
-- WHERE user_id = :user_id 
--   AND YEAR(date) = :year 
--   AND MONTH(date) = :month 
-- ORDER BY date DESC;

-- E. Mengubah Transaksi
-- UPDATE transactions 
-- SET type = :type, category = :category, amount = :amount, note = :note, date = :date 
-- WHERE id = :id AND user_id = :user_id;

-- F. Menghapus Transaksi
-- DELETE FROM transactions 
-- WHERE id = :id AND user_id = :user_id;

-- G. Mengambil Persentase / Rincian Pengeluaran per Kategori untuk Bulan Tertentu
-- SELECT category, SUM(amount) as total_amount
-- FROM transactions 
-- WHERE user_id = :user_id 
--   AND type = 'expense' 
--   AND YEAR(date) = :year 
--   AND MONTH(date) = :month 
-- GROUP BY category 
-- ORDER BY total_amount DESC;
