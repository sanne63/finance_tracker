from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ==========================================
# MANAJEMEN USER
# ==========================================

def create_user(name, email, password):
    conn = get_connection()
    password_hash = generate_password_hash(password)
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        cursor = conn.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error create_user: {e}")
        return None
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
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
        conn.close()


# ==========================================
# TRANSAKSI
# ==========================================

def add_transaction(user_id, type, category, amount, note, date):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO transactions (user_id, type, category, amount, note, date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, type, category, amount, note, date)
        )
        conn.commit()
    finally:
        conn.close()

def get_all_transactions(user_id):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()

def update_transaction(user_id, id, type, category, amount, note, date):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE transactions SET type=?, category=?, amount=?, note=?, date=? WHERE id=? AND user_id=?",
            (type, category, amount, note, date, id, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def delete_transaction(user_id, id):
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM transactions WHERE id=? AND user_id=?",
            (id, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_total_summary(user_id):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type='income'",
            (user_id,)
        )
        income = cursor.fetchone()["total"]

        cursor = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type='expense'",
            (user_id,)
        )
        expense = cursor.fetchone()["total"]

        cursor = conn.execute(
            "SELECT COUNT(id) as total_count FROM transactions WHERE user_id = ?",
            (user_id,)
        )
        count = cursor.fetchone()["total_count"]

        return float(income), float(expense), int(count)
    finally:
        conn.close()

def get_monthly_summary(user_id, year, month):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE user_id = ? AND type='income'
            AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """,
            (user_id, str(year), str(month).zfill(2))
        )
        income = cursor.fetchone()["total"]

        cursor = conn.execute(
            """
            SELECT COALESCE(SUM(amount), 0) as total
            FROM transactions
            WHERE user_id = ? AND type='expense'
            AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            """,
            (user_id, str(year), str(month).zfill(2))
        )
        expense = cursor.fetchone()["total"]

        return float(income), float(expense)
    finally:
        conn.close()

def get_transactions_by_month(user_id, year, month):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT * FROM transactions
            WHERE user_id = ?
            AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            ORDER BY date DESC, id DESC
            """,
            (user_id, str(year), str(month).zfill(2))
        )
        return cursor.fetchall()
    finally:
        conn.close()

def get_category_spending(user_id, year, month):
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT category, SUM(amount) as total
            FROM transactions
            WHERE user_id = ? AND type='expense'
            AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (user_id, str(year), str(month).zfill(2))
        )
        return cursor.fetchall()
    finally:
        conn.close()