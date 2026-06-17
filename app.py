from flask import Flask, render_template

app = Flask(__name__)

# Data produk saja
produk = [
    {"id": 1, "nama": "Kuota Smartfren 4GB", "harga": 22000},
    {"id": 2, "nama": "Kuota Smartfren 10GB", "harga": 22000},
    {"id": 3, "nama": "Alight Motion Premium", "harga": 7000},
    {"id": 4, "nama": "Kuota 700MB/Hari Unlimited (28 Hari)", "harga": 67000}
]

@app.route("/")
def utama():
    return render_template("index.html", produk=produk)

# Wajib untuk Vercel
if __name__ == "__main__":
    app.run()
