## Terakhir

- Ngolah sinyal pake RPPG

-- 2 Pipeline

1. Dapetin sinyal RPPG

- POS
- GREEN / CHROM / dll

2. Asesmen stress nya sendiri itu gimana?

- Rangkuman penelitian HRV - Stress itu gini biasanya
- Dataset ECG / PPG
- Baseline (istirahat) ama tugas (stressor)
- HRV dari detak jantung diambil feature time / freq ama non linear domain
- Dilempar ke model
- Selesai dapat akurasi berapa

- Dataset itu minimal 5 menitan

3. Penelitian juga soal UST (Ultra Short Term) HRV

- Dataset dengan waktu yang pendek (1 menit) dibandingin ama yang sekitar lebih lama (3 - 5 menit)
- Korelasi pake pearson buat liat trendnya.
- Bland-altman plot buat liat perbedaan datanya buat liat limit of aggrementnya.

Kita bisa pake itu.

Stress itu relative

4. Asesmen stress itu sendiri.

- Ketika dipakai ke real-time
- Index Stress : Baevsky Stress Index
- Bikin Sendiri asesmen stressnya:
- Real-time
  - Ambil 1-2 menit buat baseline, asumsikan aja lagi kondisi santai
  - Untuk menit selanjutnya (2-4) itu dijadikan sebagai stressor,
  - Misalkan nilainya seperti kurang 30% dari baseline, itu stress.
