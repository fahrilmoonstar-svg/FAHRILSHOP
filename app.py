from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
import random
import aiohttp
import asyncio

app = Flask(__name__)
app.secret_key = "fahrilshop_2026"

# ===================== FUNGSI HEADER ACAK =====================
def create_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, seperti Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 seperti Mac OS X) AppleWebKit/605.1.15 (KHTML, seperti Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
    ]
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    return headers

# ===================== DATA PRODUK =====================
DATA = {
    "produk": [
        {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia", "masa": "30 Hari", "ket": "Data Utama"},
        {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000, "stok": 999, "status": "Selalu Tersedia", "masa": "30 Hari", "ket": "Data Utama"},
        {"id": 3, "nama": "Alight Motion Premium", "harga": 7000, "stok": 999, "status": "Selalu Tersedia", "masa": "1 Tahun", "ket": "Tanpa Watermark"},
        {"id": 4, "nama": "Kuota 700MB/Hari Unlimited (28 Hari)", "harga": 67000, "stok": 999, "status": "Selalu Tersedia", "masa": "28 Hari", "ket": "Aktif Setiap Hari"}
    ],
    "pesanan": []
}

# ===================== FUNGSI LINK WHATSAPP =====================
def buat_link_wa(nama_produk, harga, masa, ket):
    nomor_admin = "62882020654074"
    pesan = f"""Halo Admin 👋
Saya mau pesan:

🎬 {nama_produk}
📅 Masa Aktif: {masa}
💰 Harga: Rp {harga:,}
✅ Keterangan: {ket}

Terima Kasih"""
    link = f"https://wa.me/{nomor_admin}?text={pesan.replace(' ', '%20').replace('\n', '%0A')}"
    return link

# ===================== RUTE HALAMAN =====================
@app.route("/", methods=["GET", "POST"])
def halaman_utama():
    hasil = None
    link_wa = None
    if request.method == "POST":
        try:
            id_produk = int(request.form.get("produk", 0))
            jumlah = int(request.form.get("jumlah", 1))
            diskon = int(request.form.get("diskon", 0))
            barang = next((p for p in DATA["produk"] if p["id"] == id_produk), None)
            if barang:
                total = barang["harga"] * jumlah * (100 - diskon) // 100
                pesanan_baru = {
                    "id": len(DATA["pesanan"]) + 1,
                    "produk": barang["nama"],
                    "jumlah": jumlah,
                    "harga": barang["harga"],
                    "diskon": diskon,
                    "total": total,
                    "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                DATA["pesanan"].append(pesanan_baru)
                link_wa = buat_link_wa(barang["nama"], total, barang["masa"], barang["ket"])
                hasil = pesanan_baru
        except:
            pass
    return render_template("index.html", produk=DATA["produk"], hasil=hasil, link_wa=link_wa)

# ===================== HALAMAN LOGIN ERLS COMMUNITY =====================
@app.route("/login-erls")
def halaman_login_erls():
    return render_template("login_erls.html")

@app.route("/proses-login", methods=["POST"])
def proses_login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    # Cek syarat login
    if username.strip() == "":
        return render_template("login_erls.html", pesan="⚠️ ISI USERNAME DULU!", warna="#ff4444")
    if password == "":
        return render_template("login_erls.html", pesan="⚠️ ISI PASSWORD DULU!", warna="#ff4444")
    if len(password) < 6:
        return render_template("login_erls.html", pesan="⚠️ PASSWORD MINIMAL 6 KARAKTER!", warna="#ffbb33")
    
    # Jika berhasil
    return render_template("login_erls.html", pesan="✅ BERHASIL LOGIN MEMUAT DATA!", warna="#00C851")

# ===================== HALAMAN ADMIN =====================
@app.route("/login", methods=["GET", "POST"])
def halaman_login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "fahril123":
            session["masuk"] = True
            flash("Berhasil masuk ke panel admin")
            return redirect(url_for("halaman_kelola"))
        flash("❌ Username atau Password salah!")
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
                masa = request.form.get("masa", "-")
                ket = request.form.get("ket", "-")
                if nama and harga > 0:
                    id_baru = max(p["id"] for p in DATA["produk"]) + 1 if DATA["produk"] else 1
                    status = "Selalu Tersedia" if stok >= 999 else ("Tersedia" if stok > 0 else "Habis")
                    DATA["produk"].append({
                        "id": id_baru, "nama": nama, "harga": harga, "stok": stok,
                        "status": status, "masa": masa, "ket": ket
                    })
                    flash("✅ Produk berhasil ditambahkan")
            elif aksi == "hapus":
                id_produk = int(request.form.get("id", 0))
                DATA["produk"] = [p for p in DATA["produk"] if p["id"] != id_produk]
                flash("🗑️ Produk berhasil dihapus")
        except:
            flash("❌ Gagal memproses data")
        return redirect(url_for("halaman_kelola"))
    return render_template("kelola.html", produk=DATA["produk"])

@app.route("/laporan")
def halaman_laporan():
    if not session.get("masuk"):
        return redirect(url_for("halaman_login"))
    periode = request.args.get("periode", "semua")
    daftar = DATA["pesanan"]
    if periode == "hari":
        hari_ini = datetime.now().strftime("%Y-%m-%d")
        daftar = [p for p in daftar if p["waktu"].startswith(hari_ini)]
    elif periode == "bulan":
        bulan_ini = datetime.now().strftime("%Y-%m")
        daftar = [p for p in daftar if p["waktu"].startswith(bulan_ini)]
    total_pendapatan = sum(p["total"] for p in daftar)
    return render_template("laporan.html", daftar=daftar, total=total_pendapatan, periode=periode)

# ===================== HALAMAN GAME & KONTROL =====================
@app.route("/game")
def halaman_game():
    return render_template("game.html")

@app.route("/control")
def halaman_control():
    return render_template("control.html")

@app.route("/logout")
def halaman_keluar():
    session.pop("masuk", None)
    return redirect(url_for("halaman_utama"))
