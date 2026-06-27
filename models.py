from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# MANAJEMEN USER
# ==========================================

def create_user(name, email, password):
    """
    Mendaftarkan user baru ke database.
    Password di-hash demi keamanan sebelum disimpan.
    """
    conn = get_connection()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
            (name, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error create_user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def authenticate_user(email, password):
    """
    Memeriksa email dan password user.
    Mengembalikan data user jika valid, atau None jika tidak cocok.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        return None
    except Exception as e:
        print(f"Error authenticate_user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


# ==========================================
# TRANSAKSI (DIBATASI PER USER)
# ==========================================

def add_transaction(user_id, type, category, amount, note, date):
    """Menambahkan transaksi baru yang terikat pada user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, type, category, amount, note, date)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_all_transactions(user_id):
    """Mengambil seluruh transaksi milik user tertentu."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC, id DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_transaction(user_id, id, type, category, amount, note, date):
    """Mengupdate data transaksi tertentu jika transaksi tersebut milik user tersebut."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE transactions SET type=%s, category=%s, amount=%s, note=%s, date=%s WHERE id=%s AND user_id=%s",
            (type, category, amount, note, date, id, user_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def delete_transaction(user_id, id):
    """Menghapus transaksi tertentu milik user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM transactions WHERE id=%s AND user_id=%s",
            (id, user_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_total_summary(user_id):
    """
    Mengambil ringkasan total saldo keseluruhan untuk user.
    Mengembalikan (total_income, total_expense, total_count).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = %s AND type='income'",
            (user_id,)
        )
        income = cursor.fetchone()["COALESCE(SUM(amount), 0)"]
        
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE user_id = %s AND type='expense'",
            (user_id,)
        )
        expense = cursor.fetchone()["COALESCE(SUM(amount), 0)"]
        
        cursor.execute(
            "SELECT COUNT(id) as total_count FROM transactions WHERE user_id = %s",
            (user_id,)
        )
        count = cursor.fetchone()["total_count"]
        
        return float(income), float(expense), int(count)
    finally:
        cursor.close()
        conn.close()

def get_monthly_summary(user_id, year, month):
    """
    Mengambil ringkasan pemasukan dan pengeluaran user pada bulan dan tahun tertentu.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE user_id = %s AND type='income' AND YEAR(date) = %s AND MONTH(date) = %s
            """,
            (user_id, year, month)
        )
        income = cursor.fetchone()["total"]
        
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total 
            FROM transactions 
            WHERE user_id = %s AND type='expense' AND YEAR(date) = %s AND MONTH(date) = %s
            """,
            (user_id, year, month)
        )
        expense = cursor.fetchone()["total"]
        
        return float(income), float(expense)
    finally:
        cursor.close()
        conn.close()

def get_transactions_by_month(user_id, year, month):
    """Mengambil transaksi milik user pada tahun dan bulan tertentu."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT * FROM transactions 
            WHERE user_id = %s AND YEAR(date) = %s AND MONTH(date) = %s 
            ORDER BY date DESC, id DESC
            """,
            (user_id, year, month)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_category_spending(user_id, year, month):
    """
    Mengambil rincian pengeluaran per kategori untuk bulan tertentu,
    diurutkan dari pengeluaran terbesar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT category, SUM(amount) as total 
            FROM transactions 
            WHERE user_id = %s AND type='expense' AND YEAR(date) = %s AND MONTH(date) = %s 
            GROUP BY category 
            ORDER BY total DESC
            """,
            (user_id, year, month)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()