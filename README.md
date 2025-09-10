## Tugas Akhir

### Latar Belakang

Stress merupakan salah satu indikator krusial dalam kehidupan modern manusia. Umumnya, asesmen stres dilakukan secara subjektif melalui kuesioner atau wawancara, yang bisa dipengaruhi oleh persepsi individu. Karena stres bersifat relatif dan tidak selalu disadari oleh individu, pendekatan ini menjadi kurang andal dalam beberapa situasi.

Namun bagaimana jika menggunakan sinyal fisiologi tubuh sebagai indikator kondisi seseorang? Salah satu contohnya adalah penggunaan Sinyal Denyut Nadi (_Pulse Rate_) dan Variabilitas Antar Detak Jantung (_Heart Rate Variability_).

### Landasan Teori

HRV sendiri menjelaskan tentang seberapa banyak, jarak antar detak jantung berubah-ubah.

Maksud dari pernyataaan ini adalah, ketika kamu memiliki kondisi detak jantung 60 detak per menit (60 BPM). Jarak antara satu detak jantung ke detak jantung yang lain tidak selalu sama persis (misalnya dari detak 1 ke detak 2 sekitar 0.9 detik, dan dari detak 2 ke detak 3 sekitar 0.8 detik).

Konsep perubahan ini disebut dengan HRV.

Konsep HRV sendiri berkaitan tentang kondisi detak jantung dan dan sistem saraf tubuh.

- Ketika tubuh sedang dalam kondisi beristirahat / santai, tubuh akan menjalankan mode sistem saraf parasimpatik, menurunkan detak jantung dan meningkatkan jarak antar detak jantung untuk tubuh dapat beristirahat
- Ketika tubuh sedang dalam tekanan / melakukan tugas kognitif mental, tubuh akan menjalankan mode sistem saraf simpatik, meningkatkan detak jantung, dan menuruntkan jarak antar detak jantung agar tubuh dapat bersiap untuk menghadapi tantangan.

### Metrik HRV

HRV bukanlah sebuah nilai, melaikan koleksi dari beberapa metrik yang menunjukan perubahan waktu detak jantung, berikut beberapa metriknya

### Time Domain: Melakukan analisis perubahan waktu antara detak jantung

Bagian ini berfokus untuk mencari tahu variasi waktu antar detak jantung, dan biasa di kenal dengan konsep NN (_Normal to Normal_) interval
| **Domain** | **HRV Feature** | **Unit** | **Description** |
|----------------|------------------|----------|----------------------------------------------------------------------------------|
| **Time** | SDNN | milidetik (ms) | Mengukur seberapa besar variasi jarak antar detak jantung (standar deviasi dari seluruh data). |
| | RMSSD | milidetik (ms) | Mengukur seberapa besar perubahan antara setiap detak jantung secara berurutan. Nilai ini juga menunjukan tingkat rileks tubuh, semakin besar nilai intervalnya, maka tubuh cenderung sedang dalam kondisi rileks |

### Remote Photoplethysmography (rPPG)

Seiring berkembangnya teknologi kamera dan pemrosesan citra (image processing), kini muncul peluang untuk memperoleh sinyal fisiologis tubuh secara non-kontak, salah satunya melalui _remote photoplethysmography_ (rPPG). Berbeda dengan sensor PPG konvensional yang ditempel langsung ke kulit, rPPG dapat menangkap informasi denyut nadi hanya dari perubahan warna halus pada wajah menggunakan kamera.

Namun, agar rPPG dapat digunakan secara luas, diperlukan validasi ilmiah untuk memastikan keakuratannya. Salah satu pendekatan yang umum dilakukan adalah dengan:

- Membandingkan sinyal rPPG dan PPG secara langsung, baik dari segi estimasi `pulse rate` (PR).
- Melakukan `analisis korelasi` atau evaluasi performa antara kedua metode untuk menilai apakah rPPG bisa menjadi alternatif yang andal dan praktis dibandingkan sensor PPG konvensional.

Penelitian ini bertujuan untuk mengevaluasi sejauh mana rPPG dapat menjadi alternatif dari PPG dalam memperoleh sinyal fisiologis, khususnya untuk memprediksi kondisi tubuh seperti saat dalam keadaan rileks atau stres, tanpa perlu kontak langsung dengan kulit.

### Subject dan Metode

Penelitian ini menggunakan dataset `UBFC-Phys`, yaitu sebuah dataset multimodal yang dirancang untuk studi psikofisiologi. Dataset ini mencakup `rekaman video wajah` serta sinyal fisiologis (seperti PPG) dari partisipan yang menjalani dua skenario berbeda:

- Skenario istirahat (rest) — merepresentasikan kondisi rileks.
- Skenario tugas aritmatika mental — dirancang untuk memicu stres kognitif.

Data sinyal fisiologis akan digunakan untuk mengekstraksi `detak jantung` (pulse rate) dan fitur-fitur Heart Rate Variability (HRV).

Proses ekstraksi dan analisis sinyal dilakukan menggunakan Python, dengan bantuan library seperti `scipy` dan `neurokit2` untuk perhitungan statistik dan fitur HRV.

### Pengembangan Sistem

Berdasarkan hasil studi korelasi sebelumnya, disimpulkan bahwa metode remote photoplethysmography (rPPG) cukup andal untuk estimasi Pulse Rate (PR), tetapi belum akurat untuk fitur HRV yang lebih kompleks karena keterbatasan teknis seperti noise dan artefak gerakan.

Namun, sistem prediksi stres masih dapat dikembangkan berdasarkan perubahan Pulse Rate antar kondisi, dengan membandingkan `PR` antara kondisi istirahat `(rest)` dan kondisi `stres` (dalam hal ini, tugas aritmatika mental sebagai stressor).

Untuk metode rPPG sendiri, karena hanya Pulse Rate yang memiliki korelasi yang paling bagus dengan GT, metode `POS` akan dipakai dalam aplikasi real-time, tidak ada alasan spesifik, karena semua metode kurang lebih mirip
