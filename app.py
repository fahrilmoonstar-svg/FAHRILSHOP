from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fahrilshop_rahasia_aman_2026"

# --------------------------
# PENGATURAN JSONBIN
# --------------------------
JSONBIN_API_KEY = "$2a$10$M01dj/p0yWrQV/oc0eit3OAvXcv0RRpFKRhaQLCXyx1WtISFCX2"
JSONBIN_ID = "6a3208f4f5f4af5e29ff1a68"
HEADERS = {
    "X-Access-Key": JSONBIN_API_KEY,
    "Content-Type": "application/json"
}

# --------------------------
# FUNGSI BACA & SIMPAN DATA
# --------------------------
def baca_data():
    try:
        res = requests.get(f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}", headers=HEADERS)
        if res.status_code == 200:
            return res.json()["record"]
        else:
            return {
                "produk": [
                    {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
                    {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
                    {"id": 3, "nama": "Alight Motion Premium", "harga": 7000, "stok": 999, "status": "Selalu Tersedia"},
                    {"id": 4, "nama": "Kuota 700MB/Hari Unlimited (28 Hari)", "harga": 67000, "stok": 999, "status": "Selalu Tersedia"}
                ],
                "pesanan": []
            }
    except:
        return {
            "produk": [
                {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
                {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
                {"id": 3, "nama": "Alight Motion Premium", "harga": 7000, "stok": 999, "status": "Selalu Tersedia"},
                {"id": 4, "nama": "Kuota 700MB/Hari Unlimited (28 Hari)", "harga": 67000, "stok": 999, "status": "Selalu Tersedia"}
            ],
            "pesanan": []
        }

def simpan_data(data):
    try:
        requests.put(f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}", json=data, headers=HEADERS)
    except Exception as e:
        print("Gagal simpan ke JsonBin:", e)

# --------------------------
# FUNGSI LAPORAN
# --------------------------
def buat_laporan(periode="semua"):
    data = baca_data()
    laporan = data.get("pesanan", [])
    if periode != "semua":
        hari_ini = datetime.now().strftime("%Y-%m-%d")
        if periode == "hari":
            laporan = [p for p in laporan if p["waktu"].startswith(hari_ini)]
        elif periode == "bulan":
            bulan_ini = datetime.now().strftime("%Y-%m")
            laporan = [p for p in laporan if p["waktu"].startswith(bulan_ini)]
    total = sum(p["total"] for p in laporan)
    return {"daftar": laporan, "total": total}

# --------------------------
# RUTE HALAMAN
# --------------------------
@app.route("/", methods=["GET", "POST"])
def utama():
    data = baca_data()
    if request.method == "POST":
        id_produk = int(request.form["produk"])
        jumlah = int(request.form.get("jumlah", 1))
        diskon = int(request.form.get("diskon", 0))
        barang = next((p for p in data["produk"] if p["id"] == id_produk), None)
        if barang:
            harga_satuan = barang["harga"]
            total_sebelum = harga_satuan * jumlah
            potongan = total_sebelum * diskon // 100
            total_bayar = total_sebelum - potongan
            pesanan = {
                "id": len(data["pesanan"]) + 1,
                "produk": barang["nama"],
                "jumlah": jumlah,
                "harga_satuan": harga_satuan,
                "diskon": diskon,
                "total": total_bayar,
                "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            data["pesanan"].append(pesanan)
            simpan_data(data)
            return render_template("index.html", produk=data["produk"], hasil=pesanan)
    return render_template("index.html", produk=data["produk"])

@app.route("/login", methods=["GET", "POST"])
def masuk():
    if request.method == "POST":
        user = request.form["username"]
        sandi = request.form["password"]
        if user == "admin" and sandi == "fahril123":
            session["masuk"] = True
            flash("✅ Berhasil masuk ke panel admin")
            return redirect(url_for("kelola"))
        flash("❌ Username atau password salah!")
    return render_template("login.html")

@app.route("/kelola", methods=["GET", "POST"])
def kelola():
    if not session.get("masuk"):
        return redirect(url_for("masuk"))
    data = baca_data()
    produk = data["produk"]
    if request.method == "POST":
        aksi = request.form["aksi"]
        if aksi == "tambah":
            baru = {
                "id": max(p["id"] for p in produk) + 1 if produk else 1,
                "nama": request.form["nama"].strip(),
                "harga": int(request.form["harga"]),
                "stok": int(request.form["stok"]),
                "status": "Selalu Tersedia" if int(request.form["stok"]) == 999 else ("Tersedia" if int(request.form["stok"]) > 0 else "Habis")
            }
            produk.append(baru)
            flash("✅ Produk berhasil ditambahkan")
        elif aksi == "ubah":
            brg = next(x for x in produk if x["id"] == int(request.form["id"]))
            brg["nama"] = request.form["nama"].strip()
            brg["harga"] = int(request.form["harga"])
            brg["stok"] = int(request.form["stok"])
            brg["status"] = "Selalu Tersedia" if brg["stok"] == 999 else ("Tersedia" if brg["stok"] > 0 else "Habis")
            flash("✅ Produk berhasil diperbarui")
        elif aksi == "hapus":
            data["produk"] = [x for x in produk if x["id"] != int(request.form["id"])]
            flash("🗑️ Produk berhasil dihapus")
        simpan_data(data)
        return redirect(url_for("kelola"))
    return render_template("kelola.html", produk=produk)

@app.route("/laporan")
def lap():
    if not session.get("masuk"):
        return redirect(url_for("masuk"))
    periode = request.args.get("periode", "semua")
    return render_template("laporan.html", laporan=buat_laporan(periode), periode=periode)

@app.route("/logout")
def keluar():
    session.pop("masuk", None)
    flash("👋 Berhasil keluar")
    return redirect(url_for("utama"))

if __name__ == "__main__":
    app.run()
