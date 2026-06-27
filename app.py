from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, date
import models
from database import init_db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Inisialisasi Database saat aplikasi dijalankan
with app.app_context():
    init_db()

# ==========================================
# WEB ROUTING (HALAMAN)
# ==========================================

@app.route('/')
def index():
    """Mengalihkan ke dashboard jika sudah login, atau ke login jika belum."""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    """Menampilkan halaman login."""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/register')
def register():
    """Menampilkan halaman registrasi."""
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Menampilkan dashboard keuangan."""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])


# ==========================================
# API ROUTING (AUTHENTICATION)
# ==========================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not name or not email or not password:
        return jsonify({"success": False, "message": "Semua data harus diisi!"}), 400
        
    if len(password) < 6:
        return jsonify({"success": False, "message": "Kata sandi minimal 6 karakter!"}), 400
        
    user_id = models.create_user(name, email, password)
    if user_id:
        return jsonify({"success": True, "message": "Registrasi berhasil! Silakan login."})
    else:
        return jsonify({"success": False, "message": "Email sudah terdaftar atau terjadi kesalahan."}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"success": False, "message": "Email dan kata sandi harus diisi!"}), 400
        
    user = models.authenticate_user(email, password)
    if user:
        session['user'] = user
        return jsonify({"success": True, "message": "Login berhasil!"})
    else:
        return jsonify({"success": False, "message": "Email atau kata sandi salah."}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logout berhasil!"})

@app.route('/api/me', methods=['GET'])
def api_me():
    if 'user' in session:
        return jsonify({"authenticated": True, "user": session['user']})
    return jsonify({"authenticated": False}), 401


# ==========================================
# API ROUTING (TRANSAKSI)
# ==========================================

@app.route('/api/transactions', methods=['GET'])
def api_get_transactions():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user']['id']
    
    # Ambil filter dari query parameter
    tx_type = request.args.get('type', 'all') # all, income, expense
    search = request.args.get('search', '').strip().lower()
    year = request.args.get('year')
    month = request.args.get('month')
    
    # Jika year dan month dikirimkan, filter bulanan. Jika tidak, ambil semua.
    if year and month:
        rows = models.get_transactions_by_month(user_id, int(year), int(month))
    else:
        rows = models.get_all_transactions(user_id)
        
    filtered = []
    for r in rows:
        # Filter tipe transaksi
        if tx_type != 'all' and r['type'] != tx_type:
            continue
            
        # Filter kata kunci pencarian
        if search:
            cat_match = search in r['category'].lower()
            note_match = (r['note'] and search in r['note'].lower()) or False
            if not (cat_match or note_match):
                continue
                
        # Konversi objek Row ke Dictionary dan formatting tipe data untuk JSON
        item = dict(r)
        if isinstance(item['date'], (date, datetime)):
            item['date'] = item['date'].strftime('%Y-%m-%d')
        else:
            item['date'] = str(item['date'])
        item['amount'] = float(item['amount'])
        filtered.append(item)
        
    return jsonify(filtered)

@app.route('/api/transactions', methods=['POST'])
def api_add_transaction():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user']['id']
    data = request.get_json() or {}
    
    tx_type = data.get('type')
    category = data.get('category', '').strip()
    amount = data.get('amount')
    note = data.get('note', '').strip()
    date_str = data.get('date')
    
    if not tx_type or not category or amount is None or not date_str:
        return jsonify({"success": False, "message": "Data transaksi tidak lengkap!"}), 400
        
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return jsonify({"success": False, "message": "Jumlah transaksi harus lebih besar dari 0!"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Format jumlah transaksi tidak valid!"}), 400
        
    models.add_transaction(user_id, tx_type, category, amount_val, note or None, date_str)
    return jsonify({"success": True, "message": "Transaksi berhasil ditambahkan."})

@app.route('/api/transactions/<int:tx_id>', methods=['PUT'])
def api_update_transaction(tx_id):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user']['id']
    data = request.get_json() or {}
    
    tx_type = data.get('type')
    category = data.get('category', '').strip()
    amount = data.get('amount')
    note = data.get('note', '').strip()
    date_str = data.get('date')
    
    if not tx_type or not category or amount is None or not date_str:
        return jsonify({"success": False, "message": "Data transaksi tidak lengkap!"}), 400
        
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            return jsonify({"success": False, "message": "Jumlah transaksi harus lebih besar dari 0!"}), 400
    except ValueError:
        return jsonify({"success": False, "message": "Format jumlah transaksi tidak valid!"}), 400
        
    models.update_transaction(user_id, tx_id, tx_type, category, amount_val, note or None, date_str)
    return jsonify({"success": True, "message": "Transaksi berhasil diperbarui."})

@app.route('/api/transactions/<int:tx_id>', methods=['DELETE'])
def api_delete_transaction(tx_id):
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user']['id']
    models.delete_transaction(user_id, tx_id)
    return jsonify({"success": True, "message": "Transaksi berhasil dihapus."})

@app.route('/api/summary', methods=['GET'])
def api_get_summary():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user_id = session['user']['id']
    
    year_str = request.args.get('year')
    month_str = request.args.get('month')
    
    if not year_str or not month_str:
        now = datetime.now()
        year = now.year
        month = now.month
    else:
        try:
            year = int(year_str)
            month = int(month_str)
        except ValueError:
            now = datetime.now()
            year = now.year
            month = now.month
            
    # Ambil ringkasan keseluruhan
    total_inc, total_exp, total_count = models.get_total_summary(user_id)
    total_saldo = total_inc - total_exp
    
    # Ambil ringkasan bulanan
    monthly_inc, monthly_exp = models.get_monthly_summary(user_id, year, month)
    
    # Ambil rincian pengeluaran per kategori
    cat_spending_raw = models.get_category_spending(user_id, year, month)
    category_spending = []
    for c in cat_spending_raw:
        category_spending.append({
            "category": c["category"],
            "total": float(c["total"])
        })
        
    return jsonify({
        "total_saldo": total_saldo,
        "total_transactions_count": total_count,
        "monthly_income": monthly_inc,
        "monthly_expense": monthly_exp,
        "category_spending": category_spending
    })

if __name__ == '__main__':
    # Jalankan Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
