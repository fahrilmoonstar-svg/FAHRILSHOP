// ============================================
// ===== KODE DAFTAR BUAH (DARI GAMBAR) =====
// ============================================
const fruits = [
    "Apple",
    "Banana",
    "Mango",
    "Orange",
    "Grape",
    "Watermelon"
];

// Loop untuk mencetak buah ke console (F12)
for (let i = 0; i < fruits.length; i++) {
    console.log(fruits[i]);
}

// (Opsional) Kode untuk menampilkan list buah di layar web
// Jika Kakak ingin melihat daftar buahnya muncul di halaman web, hilangkan tanda komentar di bawah ini:
/*
const listContainer = document.createElement('ul');
listContainer.style.textAlign = 'center';
listContainer.style.listStyle = 'none';
listContainer.style.padding = '20px';
listContainer.style.color = '#e0e0e0';

fruits.forEach(fruit => {
    const li = document.createElement('li');
    li.textContent = '🍎 ' + fruit;
    li.style.padding = '5px';
    li.style.fontSize = '18px';
    listContainer.appendChild(li);
});
document.body.appendChild(listContainer);
*/
