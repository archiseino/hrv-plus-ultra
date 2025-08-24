## Tugas Akhir: Analisis Studi Korelasi rPPG dan PPG terhadap Estimasi Pulse Rate dan HRV untuk Deteksi Stress Non-Kontak Berdasarkan Kamera

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
| **Time** | MeanNN | milidetik (ms) | Rata-rata jarak waktu antar detak jantung dalam periode tertentu (misalnya 1–2 menit rekaman). |
| | SDNN | milidetik (ms) | Mengukur seberapa besar variasi jarak antar detak jantung (standar deviasi dari seluruh data). |
| | pNN50 | % | Mengukur seberapa sering jarak antar detak jantung berubah lebih dari 50ms. Semakin sering terjadi, maka artinya tubuh lebih rileks |
| | RMSSD | milidetik (ms) | Mengukur seberapa besar perubahan antara setiap detak jantung secara berurutan. Nilai ini juga menunjukan tingkat rileks tubuh, semakin besar nilai intervalnya, maka tubuh cenderung sedang dalam kondisi rileks |

## Frequency Domain: Melihat komponen frekuensi pembentuk sinyal detak jantung

Selain melihat perubahan waktu antar detak jantung, kita juga bisa melihat isi “frekuensi” di dalam sinyal detak jantung.

| **Domain**    | **HRV Feature**                     | **Unit** | **Description**                                                                                                                                                   |
| ------------- | ----------------------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frequency** | LF (Low Frequencies 0.04 - 0.15 Hz) | ms²      | Mengukur aktivitas campuran antara stres dan relaksasi (simpatik & parasimpatik), biasanya terlihat saat tubuh tidak terlalu aktif maupun terlalu santai.         |
|               | HF (High Frequencies 0.15 - 0.4 Hz) | ms²      | Mengukur aktivitas sistem saraf parasimpatik (mode rileks/istirahat). Semakin tinggi, semakin tubuh dalam kondisi tenang.                                         |
|               | LF/HF                               | -        | Perbandingan antara LF dan HF. Digunakan untuk melihat keseimbangan antara stres dan relaksasi. Nilai tinggi bisa berarti tubuh sedang lebih tertekan atau aktif. |

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

### Hasil Analsis Studi Korelasi

Berdasarkan hasil studi korelasi yang ditunjukkan pada tabel berikut, dapat disimpulkan bahwa fitur `Pulse Rate (PR)` memiliki korelasi tertinggi antara sinyal rPPG dan PPG di semua metode ekstraksi:

| Metode | Fitur | Korelasi | p-value |
| ------ | ----- | -------- | ------- |
| POS    | PR    | 0.7439   | 0.0010  |
| LGI    | PR    | 0.7681   | 0.0005  |
| OMIT   | PR    | 0.7651   | 0.0006  |
| GREEN  | PR    | 0.7846   | 0.0005  |
| CHROM  | PR    | 0.7643   | 0.0006  |

Didapatkan bahwasannya hanya rPPG mampu secara kurang lebih akurat untuk memprediksi `Pulse Rate`. Namun, untuk fitur HRV lainnya seperti `LF, HF, SDNN, pNN50, dan LF/HF`, nilai korelasi cenderung lebih rendah dan sering kali tidak signifikan secara statistik (p-value > 0.05). Ini menunjukkan bahwa akurasi estimasi fitur HRV dari sinyal rPPG belum cukup stabil atau dapat diandalkan.

Hal ini menunjukan bahwa:

- rPPG dapat digunakan secara cukup akurat untuk mengestimasi Pulse Rate, terutama dalam kondisi pencahayaan dan posisi wajah yang stabil.
- Namun, untuk estimasi fitur HRV yang lebih kompleks, dibutuhkan sinyal yang lebih bersih dan stabil seperti dari PPG langsung atau sinyal ECG, karena fitur HRV sangat sensitif terhadap noise dan artefak gerakan.
- Keterbatasan teknis seperti motion artifact, noise dari pencahayaan, serta ketidakstabilan ROI wajah menjadi tantangan utama dalam penggunaan rPPG untuk analisis HRV tingkat lanjut.

### Pengembangan Sistem

Berdasarkan hasil studi korelasi sebelumnya, disimpulkan bahwa metode remote photoplethysmography (rPPG) cukup andal untuk estimasi Pulse Rate (PR), tetapi belum akurat untuk fitur HRV yang lebih kompleks karena keterbatasan teknis seperti noise dan artefak gerakan.

Namun, sistem prediksi stres masih dapat dikembangkan berdasarkan perubahan Pulse Rate antar kondisi, dengan membandingkan `PR` antara kondisi istirahat `(rest)` dan kondisi `stres` (dalam hal ini, tugas aritmatika mental sebagai stressor).

Untuk metode rPPG sendiri, karena hanya Pulse Rate yang memiliki korelasi yang paling bagus dengan GT, metode `POS` akan dipakai dalam aplikasi real-time, tidak ada alasan spesifik, karena semua metode kurang lebih mirip

#### Penentuan Threshold

Untuk menentukan ambang batas (threshold) perubahan PR yang mengindikasikan stres, akan dilakukan dua pendekatan:

- Analisis Dataset UBFC-Phys
  Menganalisis selisih PR antara segmen kondisi rest dan stress (tugas aritmatika) yang tersedia di dataset.

- Eksperimen Langsung pada Subjek Baru
  Mengambil data dari subjek nyata dengan skenario serupa (rest dan mental stress task), menggunakan rPPG, untuk menghitung dan memvalidasi threshold.

Skenario stres akan disimulasikan melalui perekaman subjek saat mengerjakan tugas aritmatika di situs:
🔗 [react-mental-task-app.vercel.app](https://react-mental-task-app.vercel.app/)

#### Prediksi Real-Time

Dalam implementasi real-time, digunakan asumsi bahwa 2 menit pertama merepresentasikan kondisi rest, dan 2 menit berikutnya adalah stressor. Perbedaan Pulse Rate dianalisis untuk memutuskan apakah terjadi peningkatan signifikan yang menunjukkan kondisi stres.

$$
\text{PR}_{stress} = \text{PR}_{Rest} \times (1 + \frac{\Delta \%}{100})
$$

Dengan asumsi umum bahwa:

- Delta merupakan percentasi perbedaan Pulse Rate ketika dalam kondisi rest (santai) dengan stres, Berdasarkan data dari hasil dataset `UBFC-Phys` dan melakukan perekaman pada beberapa subject
- PR akan meningkat saat stres
- PR pada kondisi istirahat relatif stabil dan lebih rendah

### Rencana Tugas

- Mencari subjek dan merekam subjek dalam kondisi rest / stress
- Menghitung threshold untuk kondisi rest / stress state
- Implementasi formula dalam KivyApp
- Mencari referensi penelitian terkait sebagai pendukung

### Kesimpulan

Mungkin segini dulu yang bisa saya pikirkan pada saat ini. Pak Martin ada pendapat lain?

To be fair, karena ternyata rPPG hanya bisa melakukan estimasi Pulse Rate, karena masalah limitasi, apakah ini termasuk penelitian yang parsial gagal atau kita bisa taruh di bagian kesimpulan dan saran, menunjukan bahwa masih ada limitasi dari rppg?
