from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fahrilshop_rahasia_2026"

# --------------------------
# PENGATURAN JSONBIN
# --------------------------
# Pakai Master Key saja yang aman
JSONBIN_API_KEY = "$2a$10$EcY7eevXYKOMgUsuNSKjW.mKxnU2FcMpnAFPt5pAfQntV27ugB/Am"
# ID Bin: pastikan ini benar, kalau masih salah nanti kita ganti
JSONBIN_ID = "6a3208f4f5f4af5e29ff1a68"

HEADERS = {
    "X-Master-Key": JSONBIN_API_KEY,
    "Content-Type": "application/json"
}

# --------------------------
# FUNGSI BACA & SIMPAN DATA
# --------------------------
def baca_data():
    try:
        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"
        res = requests.get(url, headers=HEADERS, timeout=8)
        res.raise_for_status()
        data = res.json()
        return data.get("record", {
            "produk": [
                {"id":1,"nama":"Kuota Smartfren 4GB","harga":22000,"stok":999,"status":"Selalu Tersedia"},
                {"id":2,"nama":"Kuota Smartfren 10GB","harga":22000,"stok":999,"status":"Selalu Tersedia"},
                {"id":3,"nama":"Alight Motion Premium","harga":7000,"stok":999,"status":"Selalu Tersedia"},
                {"id":4,"nama":"Kuota 700MB/Hari Unlimited (28 Hari)","harga":67000,"stok":999,"status":"Selalu Tersedia"}
            ],
            "pesanan": []
        })
    except:
        # Kalau gagal akses, pakai data cadangan
        return {
            "produk": [
                {"id":1,"nama":"Kuota Smartfren 4GB","harga":22000,"stok":999,"status":"Selalu Tersedia"},
                {"id":2,"nama":"Kuota Smartfren 10GB","harga":22000,"stok":999,"status":"Selalu Tersedia"},
                {"id":3,"nama":"Alight Motion Premium","harga":7000,"stok":999,"status":"Selalu Tersedia"},
                {"id":4,"nama":"Kuota 700MB/Hari Unlimited (28 Hari)","harga":67000,"stok":999,"status":"Selalu Tersedia"}
            ],
            "pesanan": []
        }

def simpan_data(data):
    try:
        url = f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}"
        requests.put(url, json=data, headers=HEADERS, timeout=8)
    except:
        pass

# --------------------------
# FUNGSI LAPORAN
# --------------------------
def buat_laporan(periode="semua"):
    data = baca_data()
    daftar = data.get("pesanan", [])
    if periode == "hari":
        hari = datetime.now().strftime("%Y-%m-%d")
        daftar = [p for p in daftar if p.get("waktu", "").startswith(hari)]
    elif periode == "bulan":
        bulan = datetime.now().strftime("%Y-%m")
        daftar = [p for p in daftar if p.get("waktu", "").startswith(bulan)]
    total = sum(p.get("total", 0) for p in daftar)
    return {"daftar": daftar, "total": total}

# --------------------------
# RUTE HALAMAN
# --------------------------
@app.route("/", methods=["GET", "POST"])
def utama():
    data = baca_data()
    hasil = None
    if request.method == "POST":
        try:
            id_produk = int(request.form.get("produk", 0))
            jumlah = int(request.form.get("jumlah", 1))
            diskon = int(request.form.get("diskon", 0))
            barang = next((p for p in data["produk"] if p["id"] == id_produk), None)
            if barang:
                total_sebelum = barang["harga"] * jumlah
                potongan = total_sebelum * diskon // 100
                total_bayar = total_sebelum - potongan
                pesanan = {
                    "id": len(data["pesanan"]) + 1,
                    "produk": barang["nama"],
                    "jumlah": jumlah,
                    "harga_satuan": barang["harga"],
                    "diskon": diskon,
                    "total": total_bayar,
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                data["pesanan"].append(pesanan)
                simpan_data(data)
                hasil = pesanan
        except:
            pass
    return render_template("index.html", produk=data["produk"], hasil=hasil)

@app.route("/login", methods=["GET", "POST"])
def masuk():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "fahril123":
            session["masuk"] = True
            flash("Berhasil masuk")
            return redirect(url_for("kelola"))
        flash("Username/password salah")
    return render_template("login.html")

@app.route("/kelola", methods=["GET", "POST"])
def kelola():
    if not session.get("masuk"):
        return redirect(url_for("masuk"))
    data = baca_data()
    if request.method == "POST":
        try:
            aksi = request.form.get("aksi")
            if aksi == "tambah":
                baru = {
                    "id": max(p["id"] for p in data["produk"]) + 1 if data["produk"] else 1,
                    "nama": request.form.get("nama", "").strip(),
                    "harga": int(request.form.get("harga", 0)),
                    "stok": int(request.form.get("stok", 0)),
                    "status": "Selalu Tersedia" if int(request.form.get("stok", 0)) >= 999 else "Tersedia" if int(request.form.get("stok", 0)) > 0 else "Habis"
                }
                data["produk"].append(baru)
                flash("Produk ditambahkan")
            elif aksi == "ubah":
                id_produk = int(request.form.get("id", 0))
                brg = next((p for p in data["produk"] if p["id"] == id_produk), None)
                if brg:
                    brg["nama"] = request.form.get("nama", "").strip()
                    brg["harga"] = int(request.form.get("harga", 0))
                    brg["stok"] = int(request.form.get("stok", 0))
                    brg["status"] = "Selalu Tersedia" if brg["stok"] >= 999 else "Tersedia" if brg["stok"] > 0 else "Habis"
                    flash("Produk diperbarui")
            elif aksi == "hapus":
                id_produk = int(request.form.get("id", 0))
                data["produk"] = [p for p in data["produk"] if p["id"] != id_produk]
                flash("Produk dihapus")
            simpan_data(data)
        except:
            flash("Gagal memproses")
        return redirect(url_for("kelola"))
    return render_template("kelola.html", produk=data["produk"])

@app.route("/laporan")
def lap():
    if not session.get("masuk"):
        return redirect(url_for("masuk"))
    periode = request.args.get("periode", "semua")
    return render_template("laporan.html", laporan=buat_laporan(periode), periode=periode)

@app.route("/logout")
def keluar():
    session.pop("masuk", None)
    return redirect(url_for("utama"))

# Khusus Vercel: jangan pakai app.run()
