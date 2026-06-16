from flask import Flask, render_template, request, redirect, url_for, flash, session
import numpy as np
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "rahasia_fahrilshop_2026"

# --------------------------
# PENGATURAN
# --------------------------
USER_ADMIN = "admin"
PASS_ADMIN = "toko1234"
WA_ADMIN = "62882020654074"

JSONBIN_API_KEY = "$2a$10$EcY7eevXYKOMgUsuNSKjW.mKxnU2FcMpnAFPt5pAfQntV27ugB/Am"
JSONBIN_BIN_ID = "6a317de2da38895dfecadf83"
JSONBIN_URL = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"

# --------------------------
# FUNGSI DATA
# --------------------------
def baca_data():
    try:
        r = requests.get(JSONBIN_URL, headers={"X-Master-Key": JSONBIN_API_KEY}, timeout=8)
        if r.status_code == 200:
            return r.json()["record"]
    except:
        pass
    return {
        "produk": [
            {"id":0,"nama":"Kouta Smartfren 4GB - 14 Hari","harga":22000,"stok":999,"status":"Selalu Tersedia"},
            {"id":1,"nama":"Kouta Smartfren 10GB - 7 Hari","harga":22000,"stok":999,"status":"Selalu Tersedia"},
            {"id":2,"nama":"Alight Motion Premium - 1 Tahun","harga":7000,"stok":999,"status":"Selalu Tersedia"},
            {"id":3,"nama":"Kouta Smartfren 700MB/Hari - 28 Hari","harga":67000,"stok":999,"status":"Selalu Tersedia"}
        ],
        "riwayat": []
    }

def simpan_data(data):
    try:
        requests.put(JSONBIN_URL, json=data, headers={"X-Master-Key": JSONBIN_API_KEY, "Content-Type":"application/json"}, timeout=8)
        return True
    except:
        return False

def proses_vektor():
    v1 = np.array([2,4,6,8]); v2 = np.array([1,3,5,7]); v3 = np.arange(1,8)
    v4 = np.linspace(0,10,5).round(2); v5 = np.zeros(4,int); v6 = np.ones(4,int); v7 = np.random.randint(1,10,4)
    return {"v1":v1.tolist(),"v2":v2.tolist(),"v3":v3.tolist(),"v4":v4.tolist(),"v5":v5.tolist(),"v6":v6.tolist(),"v7":v7.tolist(),"gabung":np.concatenate([v1,v2,v3,v4,v5,v6,v7]).round(2).tolist()}

def buat_laporan(periode="semua"):
    data = baca_data(); riwayat = data["riwayat"]; sekarang = datetime.now()
    batas = {"hari":sekarang-timedelta(1),"minggu":sekarang-timedelta(7),"bulan":sekarang-timedelta(30)}.get(periode, None)
    rincian = [p for p in riwayat if not batas or datetime.strptime(p["waktu"],"%d-%m-%Y %H:%M") >= batas]
    return {"periode":periode,"jumlah_pesanan":len(rincian),"total_pendapatan":sum(p["total"] for p in rincian),"rincian":rincian}

# --------------------------
# RUTE HALAMAN
# --------------------------
@app.route('/', methods=["GET","POST"])
def utama():
    data = baca_data(); produk = data["produk"]; hasil = link_wa = pesan_error = None
    if request.method == "POST":
        try:
            p = next(x for x in produk if x["id"] == int(request.form["produk"]))
            jum = int(request.form["jumlah"]); dis = float(request.form["diskon"])/100
            if p["stok"] != 999 and jum > p["stok"]: raise Exception(f"Stok cuma {p['stok']}")
            total = p["harga"]*jum; pot = total*dis; akhir = int(total-pot)
            if p["stok"] != 999: p["stok"] -= jum; p["status"] = "Habis" if p["stok"]<1 else "Tersedia"
            data["riwayat"].append({"waktu":datetime.now().strftime("%d-%m-%Y %H:%M"),"produk":p["nama"],"jumlah":jum,"total":akhir})
            simpan_data(data)
            hasil = {"nama":p["nama"],"jumlah":jum,"harga_satuan":p["harga"],"diskon":round(dis*100,2),"harga_total":total,"potongan":pot,"harga_akhir":akhir}
            teks = f"Halo Admin 👋\nPesanan:\n📦 {p['nama']}\n🔢 {jum} buah\n💵 Rp {p['harga']:,}\n💰 Total: Rp {akhir:,}\nTerima kasih 🙏"
            link_wa = f"https://wa.me/{WA_ADMIN}?text={quote(teks)}"
        except Exception as e:
            pesan_error = str(e)
    return render_template("index.html", data=proses_vektor(), produk=produk, hasil=hasil, link_wa=link_wa, pesan_error=pesan_error, riwayat=data["riwayat"][-5:], WA_ADMIN=WA_ADMIN)

@app.route('/login', methods=["GET","POST"])
def masuk():
    if request.method == "POST":
        if request.form["username"] == USER_ADMIN and request.form["password"] == PASS_ADMIN:
            session["masuk"] = True; return redirect(url_for("kelola"))
        flash("❌ Salah user/sandi")
    return render_template("login.html")

@app.route('/kelola', methods=["GET","POST"])
def kelola():
    if not session.get("masuk"): return redirect(url_for("masuk"))
    data = baca_data(); produk = data["produk"]
    if request.method == "POST":
        aksi = request.form["aksi"]
        if aksi == "tambah":
            produk.append({"id":max(x["id"] for x in produk)+1,"nama":request.form["nama"].strip(),"harga":int(request.form["harga"]),"stok":int(request.form["stok"]),"status":"Selalu Tersedia" if int(request.form["stok"])==999 else "Tersedia"})
            flash("✅ Ditambahkan")
        elif aksi == "ubah":
            brg = next(x for x in produk if x["id"] == int(request.form["id"]))
            brg["nama"] = request.form["nama"].strip(); brg["harga"] = int(request.form["harga"]); brg["stok"] = int(request.form["stok"]); brg["status"] = "Selalu Tersedia" if brg["stok"]==999 else ("Tersedia" if brg["stok"]>0 else "Habis")
            flash("✅ Diperbarui")
        elif aksi == "hapus":
            data["produk"] = [x for x in produk if x["id"] != int(request.form["id"])]
            flash("🗑️ Dihapus")
        simpan_data(data); return redirect(url_for("kelola"))
    return render_template("kelola.html", produk=produk)

@app.route('/laporan')
def lap():
    if not session.get("masuk"): return redirect(url_for("masuk"))
    return render_template("laporan.html", laporan=buat_laporan(request.args.get("periode","semua")))

@app.route('/logout')
def keluar():
    session.pop("masuk",None); flash("👋 Keluar"); return redirect(url_for("utama"))

# ✅ KHUSUS VERCEL
app = app
