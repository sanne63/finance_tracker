from database import get_connection

def add_transaction(type, category, amount, note, date):
    conn = get_connection()
    conn.execute(
        "INSERT INTO transactions (type, category, amount, note, date) VALUES (?, ?, ?, ?, ?)",
        (type, category, amount, note, date)
    )
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions ORDER BY date DESC"
    ).fetchall()
    conn.close()
    return rows

def update_transaction(id, type, category, amount, note, date):
    conn = get_connection()
    conn.execute(
        "UPDATE transactions SET type=?, category=?, amount=?, note=?, date=? WHERE id=?",
        (type, category, amount, note, date, id)
    )
    conn.commit()
    conn.close()

def delete_transaction(id):
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE id=?", (id,))
    conn.commit()
    conn.close()

def get_summary():
    conn = get_connection()
    income = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='income'"
    ).fetchone()[0]
    expense = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type='expense'"
    ).fetchone()[0]
    conn.close()
    return income, expense

def get_transactions_by_month(year, month):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM transactions WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ? ORDER BY date DESC",
        (str(year), str(month).zfill(2))
    ).fetchall()
    conn.close()
    return rows