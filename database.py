import pymysql
import pymysql.cursors
from config import Config

def get_connection(use_db=True):
    """
    Mendapatkan koneksi ke server MySQL.
    Jika `use_db` bernilai True, koneksi akan langsung diarahkan ke database yang ditentukan di Config.
    """
    return pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB if use_db else None,
        port=Config.MYSQL_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def init_db():
    """
    Menginisialisasi database MySQL.
    Fungsi ini akan membuat database dan tabel-tabel yang diperlukan secara otomatis
    jika belum ada di server MySQL.
    """
    try:
        # Hubungkan ke MySQL server tanpa memilih database terlebih dahulu
        conn = get_connection(use_db=False)
        cursor = conn.cursor()
        
        # Buat database jika belum ada
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Hubungkan ke database yang telah dibuat
        conn = get_connection(use_db=True)
        cursor = conn.cursor()
        
        # Buat tabel users jika belum ada
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Buat tabel transactions jika belum ada
        cursor.execute("""
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database MySQL dan tabel berhasil diinisialisasi.")
    except Exception as e:
        print(f"Error saat menginisialisasi database MySQL: {e}")
        print("Pastikan server MySQL Anda (misal XAMPP/Laragon) aktif dan konfigurasi di config.py sudah benar.")