// Menampilkan kategori
function showCategory(id){

    let kategori = document.querySelectorAll(".category");

    kategori.forEach(function(item){
        item.style.display = "none";
    });

    document.getElementById(id).style.display = "block";

}


// Tombol pesan WhatsApp
function order(nama, harga){

    // Nomor WhatsApp Moonstar Store
    let nomor = "62882020654074";

    let pesan =
`Halo kak, saya ingin order.

Produk : ${nama}
Harga : ${harga}

Mohon diproses ya. Terima kasih.`;

    let url =
"https://wa.me/" + nomor + "?text=" + encodeURIComponent(pesan);

    window.open(url,"_blank");

}


// Pencarian produk
function searchProduct(){

    let input = document
        .getElementById("search")
        .value
        .toLowerCase();

    let cards = document.querySelectorAll(".card");

    cards.forEach(function(card){

        let text = card.innerText.toLowerCase();

        if(text.indexOf(input) > -1){
            card.style.display = "block";
        }else{
            card.style.display = "none";
        }

    });

}