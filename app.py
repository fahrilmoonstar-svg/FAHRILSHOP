from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fahrilshop_rahasia_aman_2026"

# Data toko langsung di kode
data_toko = {
    "produk": [
        {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
        {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia"},
        {"id": 3, "nama": "Alight Motion Premium", "harga": 7000, "stok": 999, "status": "Selalu Tersedia"},
        {"id": 4, "nama": "Kuota 700MB/Hari Unlimited (28 Hari)", "harga": 67000, "stok": 999, "status": "Selalu Tersedia"}
    ],
    "pesanan": []
}

@app.route("/", methods=["GET", "POST"])
def utama():
    hasil = None
    if request.method == "POST":
        try:
            id_produk = int(request.form.get("produk", 0))
            jumlah = int(request.form.get("jumlah", 1))
            diskon = int(request.form.get("diskon", 0))
            barang = next((p for p in data_toko["produk"] if p["id"] == id_produk), None)
            if barang:
                total_sebelum = barang["harga"] * jumlah
                potongan = total_sebelum * diskon // 100
                total_bayar = total_sebelum - potongan
                pesanan = {
                    "id": len(data_toko["pesanan"]) + 1,
                    "produk": barang["nama"],
                    "jumlah": jumlah,
                    "harga_satuan": barang["harga"],
                    "diskon": diskon,
                    "total": total_bayar,
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                data_toko["pesanan"].append(pesanan)
                hasil = pesanan
        except Exception as e:
            print("Error pesanan:", e)
    return render_template("index.html", produk=data_toko["produk"], hasil=hasil)

@app.route("/login", methods=["GET", "POST"])
def masuk():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == "admin" and password == "fahril123":
            session["masuk"] = True
            flash("Berhasil masuk ke panel admin")
            return redirect(url_for("kelola"))
        flash("Username atau password salah!")
    return render_template("login.html")

@app.route("/kelola", methods=["GET", "POST"])
def kelola():
    if not session.get("masuk"):
        return redirect(url_for("masuk"))
    if request.method == "POST":
        try:
            aksi = request.form.get("aksi")
            if aksi == "tambah":
                nama = request.form.get("nama", "").strip()
                harga = int(request.form.get("harga", 0))
                stok = int(request.form.get("stok", 0))
                if nama and harga > 0:
                    id_baru = max(p["id"] for p in data_toko["produk"]) + 1 if data_toko["produk"] else 1
                    status = "Selalu Tersedia" if stok >= 999 else ("Tersedia" if stok > 0 else "Habis")
                    data_toko["produk"].append({
                        "id": id_baru, "nama": nama, "harga": harga, "stok": stok, "status": status
                    })
                    flash("Produk berhasil ditambahkan")
            elif aksi == "ubah":
                id_produk = int(request.form.get("id", 0))
                brg = next((p for p in data_toko["produk"] if p["id"] == id_produk), None)
                if brg:
                    brg["nama"] = request.form.get("nama", "").strip()
                    brg["harga"] = int(request.form.get("harga", 0))
                    brg["stok"] = int(request.form.get("stok", 0))
                    brg["status"] = "Selalu Tersedia" if brg["stok"] >= 999 else ("Tersedia" if brg["stok"] > 0 else "Habis")
                    flash("Produk diperbarui")
            elif aksi == "hapus":
                id_produk = int(request.form.get("id", 0))
                data_toko["produk"] = [p for p in data_toko["produk"] if p["id"] != id_produk]
                flash("Produk dihapus")
        except Exception as e:
            print("Error kelola:", e)
            flash("Terjadi kesalahan saat memproses")
        return redirect(url_for("kelola"))
    return render_template("kelola.html", produk=data_toko["produk"])

@app.route("/laporan")
def lap():
    if not session.get("masuk"):
        return redirect(url_for("masuk"))
    periode = request.args.get("periode", "semua")
    daftar = data_toko["pesanan"]
    if periode == "hari":
        hari = datetime.now().strftime("%Y-%m-%d")
        daftar = [p for p in daftar if p.get("waktu", "").startswith(hari)]
    elif periode == "bulan":
        bulan = datetime.now().strftime("%Y-%m")
        daftar = [p for p in daftar if p.get("waktu", "").startswith(bulan)]
    total = sum(p.get("total", 0) for p in daftar)
    return render_template("laporan.html", laporan={"daftar": daftar, "total": total}, periode=periode)

@app.route("/logout")
def keluar():
    session.pop("masuk", None)
    flash("Berhasil keluar")
    return redirect(url_for("utama"))
