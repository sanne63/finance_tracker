from database import init_db
from models import add_transaction, get_all_transactions, update_transaction, delete_transaction, get_summary
from datetime import date

def print_transactions(rows):
    if not rows:
        print("\n  Belum ada transaksi.\n")
        return
    print(f"\n{'ID':<5} {'Tipe':<10} {'Kategori':<15} {'Jumlah':>12} {'Tanggal':<12} Catatan")
    print("-" * 65)
    for r in rows:
        print(f"{r['id']:<5} {r['type']:<10} {r['category']:<15} {r['amount']:>12,.0f} {r['date']:<12} {r['note'] or '-'}")
    print()

def main():
    init_db()
    while True:
        print("=" * 40)
        print("   PERSONAL FINANCE TRACKER")
        print("=" * 40)
        print("1. Tambah transaksi")
        print("2. Lihat semua transaksi")
        print("3. Update transaksi")
        print("4. Hapus transaksi")
        print("5. Ringkasan saldo")
        print("0. Keluar")
        print("=" * 40)
        choice = input("Pilih menu: ").strip()

        if choice == "1":
            type = input("Tipe (income/expense): ").strip().lower()
            if type not in ("income", "expense"):
                print("Tipe harus 'income' atau 'expense'.")
                continue
            category = input("Kategori (misal: makan, gaji, transport): ").strip()
            amount = float(input("Jumlah (Rp): ").strip())
            note = input("Catatan (opsional, Enter untuk skip): ").strip()
            today = str(date.today())
            add_transaction(type, category, amount, note or None, today)
            print("Transaksi berhasil ditambahkan.")

        elif choice == "2":
            rows = get_all_transactions()
            print_transactions(rows)

        elif choice == "3":
            rows = get_all_transactions()
            print_transactions(rows)
            id = int(input("Masukkan ID transaksi yang ingin diupdate: ").strip())
            type = input("Tipe baru (income/expense): ").strip().lower()
            category = input("Kategori baru: ").strip()
            amount = float(input("Jumlah baru (Rp): ").strip())
            note = input("Catatan baru (Enter untuk skip): ").strip()
            today = str(date.today())
            update_transaction(id, type, category, amount, note or None, today)
            print("Transaksi berhasil diupdate.")

        elif choice == "4":
            rows = get_all_transactions()
            print_transactions(rows)
            id = int(input("Masukkan ID transaksi yang ingin dihapus: ").strip())
            confirm = input(f"Yakin hapus transaksi ID {id}? (y/n): ").strip().lower()
            if confirm == "y":
                delete_transaction(id)
                print("Transaksi berhasil dihapus.")

        elif choice == "5":
            income, expense = get_summary()
            balance = income - expense
            print(f"\n  Total pemasukan  : Rp {income:,.0f}")
            print(f"  Total pengeluaran: Rp {expense:,.0f}")
            print(f"  Saldo            : Rp {balance:,.0f}\n")

        elif choice == "0":
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()