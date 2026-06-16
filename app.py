from flask import Flask, render_template, request, redirect, url_for, flash, session
import numpy as np
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "rahasia_toko_fahril_2026"

# --------------------------
# PENGATURAN LENGKAP
# --------------------------
USER_ADMIN = "admin"
PASS_ADMIN = "toko1234"
WA_ADMIN = "62882020654074"  # ✅ Nomor WA kamu sudah terpasang

# Data JSONBin kamu
JSONBIN_API_KEY = "$2a$10$EcY7eevXYKOMgUsuNSKjW.mKxnU2FcMpnAFPt5pAfQntV27ugB/Am"
JSONBIN_BIN_ID = "6a317de2da38895dfecadf83"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

# --------------------------
# Fungsi Baca & Simpan Data
# --------------------------
def baca_data():
    try:
        res = requests.get(JSONBIN_URL, headers={"X-Master-Key": JSONBIN_API_KEY}, timeout=10)
        if res.status_code == 200:
            return res.json()["record"]
    except:
        pass
    # Data cadangan jika koneksi bermasalah
    return {
        "produk": [
            {"id": 0, "nama": "Kouta Smartfren 4GB - 14 Hari", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
            {"id": 1, "nama": "Kouta Smartfren 10GB - 7 Hari", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
            {"id": 2, "nama": "Alight Motion Premium - 1 Tahun", "harga": 7000, "stok": 999, "status": "Selalu Tersedia"},
            {"id": 3, "nama": "Kouta Smartfren 700MB/Hari - 28 Hari", "harga": 67000, "stok": 999, "status": "Selalu Tersedia"}
        ],
        "riwayat": []
    }

def simpan_data(data):
    try:
        requests.put(
            JSONBIN_URL,
            json=data,
            headers={"X-Master-Key": JSONBIN_API_KEY, "Content-Type": "application/json"},
            timeout=10
        )
        return True
    except:
        return False

def proses_vektor():
    v1 = np.array([2, 4, 6, 8])
    v2 = np.array([1, 3, 5, 7])
    v3 = np.arange(1, 8)
    v4 = np.linspace(0, 10, 5).round(2)
    v5 = np.zeros(4, dtype=int)
    v6 = np.ones(4, dtype=int)
    v7 = np.random.randint(1, 10, 4)
    gabung = np.concatenate((v1, v2, v3, v4, v5, v6, v7)).round(2)
    return {
        "v1": v1.tolist(), "v2": v2.tolist(), "v3": v3.tolist(),
        "v4": v4.tolist(), "v5": v5.tolist(), "v6": v6.tolist(),
        "v7": v7.tolist(), "gabung": gabung.tolist()
    }

def buat_laporan(periode="semua"):
    data = baca_data()
    riwayat = data.get("riwayat", [])
    sekarang = datetime.now()
    hasil = []
    total = 0
    jumlah = 0

    if periode == "hari":
        batas = sekarang - timedelta(days=1)
    elif periode == "minggu":
        batas = sekarang - timedelta(days=7)
    elif periode == "bulan":
        batas = sekarang - timedelta(days=30)
    else:
        batas = None

    for p in riwayat:
        waktu = datetime.strptime(p["waktu"], "%d-%m-%Y %H:%M")
        if batas is None or waktu >= batas:
            hasil.append(p)
            total += p["total"]
            jumlah += 1

    return {"periode": periode, "jumlah_pesanan": jumlah, "total_pendapatan": total, "rincian": hasil}

# --------------------------
# Rute Halaman
# --------------------------
@app.route('/', methods=['GET', 'POST'])
def halaman_utama():
    data_vektor = proses_vektor()
    data = baca_data()
    produk = data["produk"]
    hasil = None
    link_wa = None
    pesan_error = None

    if request.method == 'POST':
        try:
            pilih_id = int(request.form['produk'])
            jumlah = int(request.form['jumlah'])
            diskon = float(request.form['diskon']) / 100

            barang = next((b for b in produk if b["id"] == pilih_id), None)
            if not barang:
                raise Exception("Produk tidak ditemukan")
            if barang["stok"] < jumlah and barang["stok"] != 999:
                raise Exception(f"Stok hanya tersisa {barang['stok']}")

            harga_total = barang["harga"] * jumlah
            potongan = harga_total * diskon
            harga_akhir = int(harga_total - potongan)

            if barang["stok"] != 999:
                barang["stok"] -= jumlah
                if barang["stok"] == 0:
                    barang["status"] = "Habis"

            catatan = {
                "waktu": datetime.now().strftime("%d-%m-%Y %H:%M"),
                "produk": barang["nama"],
                "jumlah": jumlah,
                "total": harga_akhir
            }
            data["riwayat"].append(catatan)
            simpan_data(data)

            hasil = {
                "nama": barang["nama"], "jumlah": jumlah,
                "harga_satuan": barang["harga"], "diskon": round(diskon*100,2),
                "harga_total": int(harga_total), "potongan": int(potongan),
                "harga_akhir": harga_akhir
            }

            teks = f"""Halo Admin 👋
Saya ingin memesan:

📦 Produk: {hasil['nama']}
🔢 Jumlah: {hasil['jumlah']}
💵 Harga Satuan: Rp {hasil['harga_satuan']:,}
🏷️ Diskon: {hasil['diskon']}%
💰 Total Bayar: Rp {hasil['harga_akhir']:,}

Mohon diproses ya 🙏"""
            link_wa = f"https://wa.me/{WA_ADMIN}?text={quote(teks)}"

        except Exception as e:
            pesan_error = str(e)

    return render_template(
        'index.html', data=data_vektor, produk=produk,
        hasil=hasil, link_wa=link_wa, pesan_error=pesan_error,
        riwayat=data["riwayat"][-5:], WA_ADMIN=WA_ADMIN
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER_ADMIN and request.form['password'] == PASS_ADMIN:
            session["masuk"] = True
            return redirect(url_for("kelola"))
        flash("❌ Nama atau sandi salah")
    return render_template("login.html")

@app.route('/kelola', methods=['GET', 'POST'])
def kelola():
    if not session.get("masuk"):
        return redirect(url_for("login"))
    data = baca_data()
    produk = data["produk"]

    if request.method == "POST":
        aksi = request.form["aksi"]
        if aksi == "tambah":
            baru = {
                "id": max([p["id"] for p in produk], default=-1)+1,
                "nama": request.form["nama"].strip(),
                "harga": int(request.form["harga"]),
                "stok": int(request.form["stok"]),
                "status": "Selalu Tersedia" if int(request.form["stok"])==999 else "Tersedia"
            }
            produk.append(baru)
            flash("✅ Produk ditambahkan")
        elif aksi == "ubah":
            idnya = int(request.form["id"])
            brg = next((p for p in produk if p["id"]==idnya), None)
            if brg:
                brg["nama"] = request.form["nama"].strip()
                brg["harga"] = int(request.form["harga"])
                brg["stok"] = int(request.form["stok"])
                brg["status"] = "Selalu Tersedia" if brg["stok"]==999 else ("Tersedia" if brg["stok"]>0 else "Habis")
                flash("✅ Data diperbarui")
        elif aksi == "hapus":
            idnya = int(request.form["id"])
            data["produk"] = [p for p in produk if p["id"]!=idnya]
            flash("🗑️ Produk dihapus")
        simpan_data(data)
        return redirect(url_for("kelola"))

    return render_template("kelola.html", produk=produk)

@app.route('/laporan')
def laporan():
    if not session.get("masuk"):
        return redirect(url_for("login"))
    lap = buat_laporan(request.args.get("periode", "semua"))
    return render_template("laporan.html", laporan=lap)

@app.route('/logout')
def logout():
    session.pop("masuk", None)
    flash("👋 Berhasil keluar")
    return redirect(url_for("halaman_utama"))

if __name__ == "__main__":
    app.run()
