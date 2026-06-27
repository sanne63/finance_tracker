from app import app

if __name__ == "__main__":
    print("==================================================")
    print(" MENJALANKAN WEBSITE PERSONAL FINANCE TRACKER ")
    print("==================================================")
    print("Aplikasi web aktif di: http://127.0.0.1:5000")
    print("Gunakan Ctrl+C untuk menghentikan server.")
    print("==================================================")
    
    # Jalankan server web Flask
    app.run(debug=True, host='0.0.0.0', port=5000)