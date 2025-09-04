import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def catat_transaksi(jenis, jumlah, keterangan):
    try:
        jumlah = float(jumlah)
    except ValueError:
        messagebox.showerror("Error", "Jumlah harus berupa angka.")
        return

    tanggal = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transaksi = {
        "tanggal": tanggal,
        "jenis": jenis,
        "jumlah": jumlah,
        "keterangan": keterangan
    }

    data = load_data()
    data.append(transaksi)
    save_data(data)
    update_riwayat()
    update_saldo()
    messagebox.showinfo("Sukses", f"{jenis.capitalize()} berhasil dicatat.")

def update_riwayat():
    data = load_data()
    riwayat_listbox.delete(*riwayat_listbox.get_children())
    for t in data:
        riwayat_listbox.insert('', 'end', values=(t["tanggal"], t["jenis"], "Rp{:,.2f}".format(t["jumlah"]), t["keterangan"]))

def update_saldo():
    data = load_data()
    pemasukan = sum(t["jumlah"] for t in data if t["jenis"] == "pemasukan")
    pengeluaran = sum(t["jumlah"] for t in data if t["jenis"] == "pengeluaran")
    saldo = pemasukan - pengeluaran
    saldo_label.config(text="Saldo Saat Ini: Rp{:,.2f}".format(saldo))

def tambah_pemasukan():
    catat_transaksi("pemasukan", jumlah_entry.get(), keterangan_entry.get())
    jumlah_entry.delete(0, tk.END)
    keterangan_entry.delete(0, tk.END)

def tambah_pengeluaran():
    catat_transaksi("pengeluaran", jumlah_entry.get(), keterangan_entry.get())
    jumlah_entry.delete(0, tk.END)
    keterangan_entry.delete(0, tk.END)

def get_today_summary():
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    pemasukan = sum(t["jumlah"] for t in data if t["jenis"] == "pemasukan" and t["tanggal"].startswith(today))
    pengeluaran = sum(t["jumlah"] for t in data if t["jenis"] == "pengeluaran" and t["tanggal"].startswith(today))
    saldo = pemasukan - pengeluaran
    return pemasukan, pengeluaran, saldo

def update_saldo():
    data = load_data()
    total_pemasukan = sum(t["jumlah"] for t in data if t["jenis"] == "pemasukan")
    total_pengeluaran = sum(t["jumlah"] for t in data if t["jenis"] == "pengeluaran")
    total_saldo = total_pemasukan - total_pengeluaran

    saldo_label.config(text="Saldo Saat Ini (Total): Rp{:,.2f}".format(total_saldo))

    # Update harian
    today_pemasukan, today_pengeluaran, today_saldo = get_today_summary()
    saldo_harian_label.config(
        text=(
            "Saldo Hari Ini → Pemasukan: Rp{:,.2f} | Pengeluaran: Rp{:,.2f} | Saldo: Rp{:,.2f}"
            .format(today_pemasukan, today_pengeluaran, today_saldo)
        )
    )

def hapus_transaksi():
    selected_item = riwayat_listbox.selection()
    if not selected_item:
        messagebox.showwarning("Peringatan", "Pilih transaksi yang ingin dihapus.")
        return

    konfirmasi = messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus transaksi ini?")
    if not konfirmasi:
        return

    item = riwayat_listbox.item(selected_item)
    values = item['values']
    tanggal, jenis, jumlah_str, keterangan = values
    jumlah = float(jumlah_str.replace("Rp", "").replace(",", ""))

    # Load data dan cari item yang cocok
    data = load_data()
    for i, t in enumerate(data):
        if (
            t["tanggal"] == tanggal and
            t["jenis"] == jenis and
            float(t["jumlah"]) == jumlah and
            t["keterangan"] == keterangan
        ):
            del data[i]
            break

    save_data(data)
    update_riwayat()
    update_saldo()
    messagebox.showinfo("Sukses", "Transaksi berhasil dihapus.")

# ====================== GUI ======================

root = tk.Tk()
root.title("Catatan Keuangan Harian")

# Input Frame
input_frame = tk.Frame(root, padx=10, pady=10)
input_frame.pack(fill="x")

tk.Label(input_frame, text="Jumlah (Rp):").grid(row=0, column=0, sticky="w")
jumlah_entry = tk.Entry(input_frame)
jumlah_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Keterangan:").grid(row=1, column=0, sticky="w")
keterangan_entry = tk.Entry(input_frame)
keterangan_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Button(input_frame, text="Tambah Pemasukan", command=tambah_pemasukan, bg="lightgreen").grid(row=2, column=0, pady=10)
tk.Button(input_frame, text="Tambah Pengeluaran", command=tambah_pengeluaran, bg="salmon").grid(row=2, column=1, pady=10)
tk.Button(input_frame, text="Hapus Transaksi", command=hapus_transaksi, bg="lightgray").grid(row=2, column=2, pady=10)


# Saldo
saldo_label = tk.Label(root, text="Saldo Saat Ini: Rp0.00", font=("Arial", 12, "bold"))
saldo_label.pack(pady=10)

saldo_harian_label = tk.Label(root, text="Saldo Hari Ini: -", font=("Arial", 10))
saldo_harian_label.pack(pady=(0, 10))

# Riwayat Frame
riwayat_frame = tk.Frame(root)
riwayat_frame.pack(fill="both", expand=True, padx=10, pady=10)

riwayat_listbox = ttk.Treeview(riwayat_frame, columns=("Tanggal", "Jenis", "Jumlah", "Keterangan"), show="headings")
riwayat_listbox.heading("Tanggal", text="Tanggal")
riwayat_listbox.heading("Jenis", text="Jenis")
riwayat_listbox.heading("Jumlah", text="Jumlah")
riwayat_listbox.heading("Keterangan", text="Keterangan")
riwayat_listbox.pack(fill="both", expand=True)

# Scrollbar for Riwayat
scrollbar = tk.Scrollbar(riwayat_frame, orient="vertical", command=riwayat_listbox.yview)
riwayat_listbox.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Load awal
update_riwayat()
update_saldo()

root.mainloop()
