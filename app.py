from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fahrilshop_2026"

# Data hanya ada di kode, tidak disimpan ke mana pun
DATA = {
    "produk": [
        {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
        {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
        {"id": 3, "nama": "Alight Motion Premium", "harga": 7000, "stok": 999, "status": "Selalu Tersedia"},
        {"id": 4, "nama": "Kuota 700MB/Hari Unlimited (28 Hari)", "harga": 67000, "stok": 999, "status": "Selalu Tersedia"}
    ],
    "pesanan": []
}

@app.route("/", methods=["GET", "POST"])
def halaman_utama():
    hasil = None
    if request.method == "POST":
        try:
            id_produk = int(request.form.get("produk", 0))
            jumlah = int(request.form.get("jumlah", 1))
            diskon = int(request.form.get("diskon", 0))
            barang = next((p for p in DATA["produk"] if p["id"] == id_produk), None)
            if barang:
                total = barang["harga"] * jumlah * (100 - diskon) // 100
                pesanan = {
                    "id": len(DATA["pesanan"]) + 1,
                    "produk": barang["nama"],
                    "jumlah": jumlah,
                    "harga": barang["harga"],
                    "diskon": diskon,
                    "total": total,
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                DATA["pesanan"].append(pesanan)
                hasil = pesanan
        except:
            pass
    return render_template("index.html", produk=DATA["produk"], hasil=hasil)

@app.route("/login", methods=["GET", "POST"])
def halaman_login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "fahril123":
            session["masuk"] = True
            flash("Berhasil masuk")
            return redirect(url_for("halaman_kelola"))
        flash("Username atau sandi salah")
    return render_template("login.html")

@app.route("/kelola", methods=["GET", "POST"])
def halaman_kelola():
    if not session.get("masuk"):
        return redirect(url_for("halaman_login"))
    if request.method == "POST":
        try:
            aksi = request.form.get("aksi")
            if aksi == "tambah":
                nama = request.form.get("nama", "").strip()
                harga = int(request.form.get("harga", 0))
                stok = int(request.form.get("stok", 0))
                if nama and harga > 0:
                    id_baru = max(p["id"] for p in DATA["produk"]) + 1 if DATA["produk"] else 1
                    status = "Selalu Tersedia" if stok >= 999 else ("Tersedia" if stok > 0 else "Habis")
                    DATA["produk"].append({"id": id_baru, "nama": nama, "harga": harga, "stok": stok, "status": status})
                    flash("Produk ditambahkan")
            elif aksi == "ubah":
                id_produk = int(request.form.get("id", 0))
                brg = next((p for p in DATA["produk"] if p["id"] == id_produk), None)
                if brg:
                    brg["nama"] = request.form.get("nama", "").strip()
                    brg["harga"] = int(request.form.get("harga", 0))
                    brg["stok"] = int(request.form.get("stok", 0))
                    brg["status"] = "Selalu Tersedia" if brg["stok"] >= 999 else ("Tersedia" if brg["stok"] > 0 else "Habis")
                    flash("Produk diperbarui")
            elif aksi == "hapus":
                id_produk = int(request.form.get("id", 0))
                DATA["produk"] = [p for p in DATA["produk"] if p["id"] != id_produk]
                flash("Produk dihapus")
        except:
            flash("Gagal memproses")
        return redirect(url_for("halaman_kelola"))
    return render_template("kelola.html", produk=DATA["produk"])

@app.route("/laporan")
def halaman_laporan():
    if not session.get("masuk"):
        return redirect(url_for("halaman_login"))
    periode = request.args.get("periode", "semua")
    daftar = DATA["pesanan"]
    if periode == "hari":
        hari = datetime.now().strftime("%Y-%m-%d")
        daftar = [p for p in daftar if p["waktu"].startswith(hari)]
    elif periode == "bulan":
        bulan = datetime.now().strftime("%Y-%m")
        daftar = [p for p in daftar if p["waktu"].startswith(bulan)]
    total = sum(p["total"] for p in daftar)
    return render_template("laporan.html", daftar=daftar, total=total, periode=periode)

@app.route("/logout")
def halaman_keluar():
    session.pop("masuk", None)
    return redirect(url_for("halaman_utama"))

# Tidak pakai app.run() untuk Vercel
