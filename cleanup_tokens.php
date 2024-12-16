<?php
$fileName = __DIR__ . '/tokens.json'; // Lokasi file tokens.json
$currentTime = time(); // Waktu saat ini (timestamp)

// Periksa apakah file tokens.json ada
if (!file_exists($fileName)) {
    echo "File tokens.json tidak ditemukan.\n";
    exit;
}

// Baca isi file tokens.json
$data = json_decode(file_get_contents($fileName), true);

// Periksa apakah data valid
if (!is_array($data)) {
    echo "Isi file tokens.json tidak valid.\n";
    exit;
}

// Filter data untuk menghapus token yang sudah lebih dari 60 menit
$updatedData = array_filter($data, function ($token) use ($currentTime) {
    $tokenTime = strtotime($token['timestamp']);
    return ($currentTime - $tokenTime) <= 3600; // Hanya simpan token yang kurang dari atau sama dengan 60 menit
});

// Tulis ulang file tokens.json jika ada perubahan
if (count($data) !== count($updatedData)) {
    file_put_contents($fileName, json_encode(array_values($updatedData), JSON_PRETTY_PRINT));
    echo "File tokens.json telah diperbarui.\n";
} else {
    echo "Tidak ada token yang kadaluarsa.\n";
}
?>
