# EVALUASI METODE REMOTE PHOTOPLETHYSMOGRAPHY DAN AREA WAJAH UNTUK PENGUKURAN DETAK JANTUNG DAN VARIABILITASNYA DARI VIDEO WAJAH DALAM KONTEKS AKTIVITAS KOGNITIF

Language: Bahasa Indonesia | [English](README.md)

Repository ini mendokumentasikan proyek Tugas Akhir sarjana yang mengevaluasi metode remote photoplethysmography (rPPG) terhadap sinyal referensi PPG dari UBFC-Phys.

## Gambaran Proyek

Penelitian ini mengevaluasi kualitas beberapa metode rPPG untuk mengestimasi:

- Heart Rate (HR)
- Fitur Heart Rate Variability (HRV) (SDNN, RMSSD)

Dengan menggunakan UBFC-Phys (subjek s41-s56), studi ini membandingkan beberapa metode rPPG dan strategi ROI wajah terhadap PPG kontak sebagai sinyal referensi. Hasil menunjukkan bahwa pada kondisi stasioner (T1), beberapa metode rPPG dapat menghasilkan waveform nadi dan estimasi HR yang mengikuti referensi dengan cukup baik, sehingga HR dan sebagian fitur HRV (SDNN, RMSSD) masih dapat dipakai.

Pada kondisi yang lebih aktif (T2: active, T3: arithmetic), gerakan tangan dan wajah memunculkan artefak yang lebih kuat, menurunkan kualitas waveform dan mengurangi kesesuaian terhadap sinyal referensi.

Analisis juga menunjukkan bahwa pemilihan ROI berpengaruh: kombinasi multi-ROI dapat meningkatkan robustness pada beberapa kasus, tetapi ROI tunggal yang terlokalisasi baik juga dapat mengungguli kombinasi ROI terfragmentasi tergantung skenario dan metodenya. Di seluruh skenario, terlihat peningkatan HR ringan saat skenario tugas, tetapi interpretasi perlu hati-hati karena sebagian perubahan dapat berasal dari kontaminasi motion artifact.

Karena dataset belum menyediakan anotasi kualitas sinyal referensi secara detail, studi ini merekomendasikan penggunaan modalitas akuisisi yang lebih kuat (misalnya ECG) pada penelitian lanjutan serta penambahan anotasi kualitas sinyal pada dataset publik agar evaluasi lebih reliabel.

## Struktur Folder Saat Ini

Folder dan file utama di workspace ini:

- `artifacts/`: keluaran hasil pipeline
- `dataset_numpy/`: folder dataset (subjek, source files, dan resource metode)
- `log-bimbingan/`: catatan bimbingan/progres
- `mediapipe_models/`: file model Face Detector dan Face Landmarker
- `pipeline.py`: pipeline reproducible (preprocess, metrics, evaluate)
- `rppg-extraction/`: skrip ekstraksi rPPG mentah dari video (`face_detector.py`, `face_landmarker.py`)
- `rppg_methods/`: implementasi metode (CHROM, GREEN, LGI, OMIT, POS)
- `Signalkit/`: skrip aplikasi proof-of-concept
- `Signalkit-Export/`: aset build/export dan file environment
- `utils/`: notebook analisis dan keluaran tabel

## Setup Environment

### 1. Versi Python

- Direkomendasikan: Python 3.11
- Minimum: Python 3.10

### 2. Instal Dependencies

Jalankan dari folder ini (`workflow-research`):

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Opsional (PoC app):

```bash
pip install -r Signalkit/requirements.txt
pip install -r Signalkit-Export/requirements.txt
```

### 3. Verifikasi Environment

```bash
python --version
pip --version
python -c "import numpy, scipy, pandas, matplotlib; print('core libs OK')"
```

## Persiapan Data

1. Unduh file zip UBFC-Phys dari sumber resmi.
2. Ekstrak semua arsip dataset dan susun di bawah `dataset_numpy/`.
3. Pastikan folder subjek tersedia dari `dataset_numpy/s41` sampai `dataset_numpy/s56`.

Struktur minimum yang diharapkan:

- `dataset_numpy/s41/`
- `dataset_numpy/s42/`
- ...
- `dataset_numpy/s56/`

Pada tahap ini, folder harus sudah berisi source files yang diekstrak (misalnya `.avi`, `.csv`, dan metadata) sebelum konversi rPPG menjadi `.npy`.

## Cara Menjalankan

Gunakan urutan eksekusi berikut.

### Langkah 1: Ekstrak Arsip Dataset

Pastikan semua zip UBFC-Phys sudah diekstrak terlebih dahulu dan ditempatkan ke `dataset_numpy/` seperti pada bagian Persiapan Data.

### Langkah 2: Hasilkan File rPPG `.npy` dari Video

Jalankan skrip ekstraksi untuk mentransformasi sinyal berbasis video menjadi file `.npy`.

```bash
cd rppg-extraction
python face_detector.py
python face_landmarker.py
```

### Langkah 3: Reproducible Pipeline

Pipeline memisahkan pemrosesan data dari pelaporan dan menghasilkan artifacts yang dapat dipakai ulang.

Sumber Face Landmarker:

```bash
python pipeline.py --root-path dataset_numpy --output-dir artifacts --rppg-source face_landmarker --step all
```

Sumber Face Detector:

```bash
python pipeline.py --root-path dataset_numpy --output-dir artifacts --rppg-source face_detector --step all
```

Keluaran yang dihasilkan:

- `artifacts/preprocessed/*.npy`
- `artifacts/signal_manifest.csv`
- `artifacts/metrics_long.csv`
- `artifacts/evaluation_summary.csv`

Jalankan per tahap:

```bash
python pipeline.py --root-path dataset_numpy --output-dir artifacts --rppg-source face_landmarker --step preprocess
python pipeline.py --output-dir artifacts --rppg-source face_landmarker --step metrics
python pipeline.py --output-dir artifacts --rppg-source face_landmarker --step evaluate
```

Bantuan CLI:

```bash
python pipeline.py --help
```

## Aplikasi Proof-of-Concept

Entry point utama Signalkit:

```bash
python Signalkit/v1/main.py
```

Distribusi executable (EXE) tersedia melalui release assets GitHub repository ini.

## Catatan Reproducibility

- Simpan hasil pemrosesan di `artifacts/` untuk rerun yang konsisten.
- Simpan snapshot environment jika diperlukan:

```bash
pip freeze > requirements-lock.txt
```

- Catat perubahan parameter di `log-bimbingan/`.

## Cara Sitasi

Jika Anda menggunakan repository ini untuk keperluan akademik, mohon sitasi tesis berikut:

Arsyadana Estu Aziz. (2025). EVALUASI METODE REMOTE PHOTOPLETHYSMOGRAPHY DAN AREA WAJAH UNTUK PENGUKURAN DETAK JANTUNG DAN VARIABILITASNYA DARI VIDEO WAJAH DALAM KONTEKS AKTIVITAS KOGNITIF. Program Studi Teknik Informatika, Institut Teknologi Sumatera.

### BibTeX

```bibtex
@thesis{azizEstu2025deteksi_hr_hrv,
  author       = {Arsyadana Estu Aziz},
  title        = {EVALUASI METODE REMOTE PHOTOPLETHYSMOGRAPHY DAN AREA WAJAH UNTUK PENGUKURAN DETAK JANTUNG DAN VARIABILITASNYA DARI VIDEO WAJAH DALAM KONTEKS AKTIVITAS KOGNITIF},
  school       = {Institut Teknologi Sumatera},
  year         = {2025},
  type         = {Undergraduate Thesis},
  address      = {Lampung Selatan, Indonesia},
  note         = {Program Studi Teknik Informatika}
}
```

## Lisensi

Tambahkan informasi lisensi (misalnya MIT, Apache-2.0, atau lisensi institusi).

## Ucapan Terima Kasih

- Martin Clinton Manullang, Ph.D.
- Program Studi Teknik Informatika ITERA
- R. Meziati Sabour, Y. Benezeth, P. De Oliveira, J. Chappe, F. Yang. UBFC-Phys: A Multimodal Database For Psychophysiological Studies Of Social Stress, IEEE Transactions on Affective Computing, 2021.
