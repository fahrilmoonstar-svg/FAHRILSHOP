from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "fahrilshop_2026"

# ===================== DATA PRODUK =====================
DATA = {
    "produk": [
        {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000, "stok": 999, "status": "Tersedia", "masa": "30 Hari", "ket": "Data Utama"},
        {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000, "stok": 999, "status": "Tersedia", "masa": "30 Hari", "ket": "Data Utama"},
        {"id": 3, "nama": "Alight Motion Premium", "harga": 7000, "stok": 999, "status": "Tersedia", "masa": "1 Tahun", "ket": "Tanpa Watermark"},
        {"id": 4, "nama": "Kuota Unlimited 28H", "harga": 67000, "stok": 999, "status": "Tersedia", "masa": "28 Hari", "ket": "Aktif Setiap Hari"},
        {"id": 5, "nama": "Jasa Edit Video JJ", "harga": 1000, "stok": 999, "status": "Tersedia", "masa": " - ", "ket": "Cepat & Estetik ✨"}
    ],
    "pesanan": []
}

# ===================== FUNGSI LINK WHATSAPP =====================
def buat_link_wa(nama_produk, harga):
    nomor_admin = "62882020654074"
    pesan = f"""Halo Admin 🤍
Saya mau pesan:
📦 {nama_produk}
💰 Total: Rp {harga:,}

Terima Kasih"""
    link = f"https://wa.me/{nomor_admin}?text={pesan.replace(' ', '%20').replace('\n', '%0A')}"
    return link

# ===================== RUTE UTAMA =====================
@app.route("/", methods=["GET", "POST"])
def home():
    hasil = None
    link_wa = None
    if request.method == "POST":
        id_produk = int(request.form.get("produk"))
        jumlah = int(request.form.get("jumlah", 1))
        
        barang = next(p for p in DATA["produk"] if p["id"] == id_produk)
        total_harga = barang["harga"] * jumlah
        
        hasil = {
            "nama": barang["nama"],
            "jumlah": jumlah,
            "total": total_harga
        }
        link_wa = buat_link_wa(barang["nama"], total_harga)
        
    return render_template("index.html", produk=DATA["produk"], hasil=hasil, link_wa=link_wa)

# ===================== HALAMAN LOGIN ERLS =====================
@app.route("/login-erls", methods=["GET", "POST"])
def login_erls():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if username == "erls" and password == "erls123":
            return render_template("login_erls.html", pesan="✅ BERHASIL LOGIN! DATA SEDANG DIMUAT...", warna="#00C851")
        else:
            return render_template("login_erls.html", pesan="❌ Username / Password Salah!", warna="#ff4444")
    
    return render_template("login_erls.html")

# ===================== HALAMAN ADMIN =====================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        user = request.form.get("user")
        pas = request.form.get("pass")
        if user == "admin" and pas == "fahril123":
            session["admin"] = True
            return redirect(url_for("kelola"))
        return render_template("login.html", error=True)
    return render_template("login.html")

@app.route("/kelola")
def kelola():
    if not session.get("admin"):
        return redirect(url_for("admin"))
    return render_template("kelola.html", produk=DATA["produk"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ===================== HALAMAN LAIN =====================
@app.route("/game")
def game():
    return render_template("game.html")

@app.route("/control")
def control():
    return render_template("control.html")

if __name__ == "__main__":
    app.run(debug=True)
