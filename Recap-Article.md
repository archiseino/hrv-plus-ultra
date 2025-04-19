## Hi...

- Based on the Article, it seems any paper that doing this is based on the sample signals over 5 min (Long term)
- Because of reason above, one needs to use the UST (Ultra Short Term) HRV analysis, but it's only for looking the correlation between the trend of the short one and the standard one.
- For detecting stress itself, one should define a rule for the case, since many doesn't defy anything for stress.
- ML Models? Nah we don't have many data.
- Evaluation? we can use the Bland-Altman and Pearson Correlation for commparing the short and standard one, and MAE, MSAE for comparing the original GT and PPG GT

# Notes on the Paper Article

Collection of Recap Article for TA Purpose

---

## Paper 1

---

**Name** : Experimental Verification of the Possibility of Reducing Photoplethysmography Measurement Time for Stress Index Calculation

Recap Article :

- Paper dari Seung-Gun Lee menjelaskan tentang perbedaan penggunaan time-length yang berbeda (1 min, 50 sec, 40 sec, 30 sec) dalam konteks real-time stress monitoring.
- Disini juga menggunakan sebuah asesmen stress index baru, yakni **Baevsky stress index** oleh Roman M.
- Metode evaluasi dari paper ini juga menggunakan R^2, koefisien perbandingan dari hrv UST (Ultra Short Term) dengan **gold standard 5 menit** dengan koef R^2 >= 0.6 yang digunakan dalam proses regresi Extra Trees Regressor.
- Evaluasi juga bagus, dengan nilai R^2 diatas 30 detik dengan R^2 minimal 0.9 menunjukan bahwa trendnya sama dengan nilai gold-standard

Personal Statements:

- Paper ini sudah cukup bagus untuk melakukan asesmen stress, bahkan dengna menggunakan index stress agar konsisten, bisa menjadi rujukan untuk metodologi.

Reference other paper that still relevant.

- Stress merupakan sebuah issue yang sedang berkembang, menurut WHO, stress-related productivity menyebabkan damage / kerugian $1 triliun usd setiap tahun, dan 15% pekerja dewasa menderita stress. [World Health Organization. Mental Health in the Workplace. 2022](https://www.who.int/teams/mentalhealth-and-substance-use/promotion-prevention/mental-health-in-the-workplace)
- Stress dapat menyebabkan masalah mental dan fisikal, menybabkan penyakit jantung, diabetes, depression, dan penyakit lainnya [Stress detection and management: A survey of wearable smart health devices](https://ieeexplore.ieee.org/document/8048734).
- Secara umum, assesmen stress dilakukan secara tradisional, melalui survey, wawancara [Perceived stress scale: Reliability
  and validity study in Greece](https://www.ncbi.nlm.nih.gov/pubmed/21909307)
- Sekarang Wearble device dapat digunakan untuk melihat sinyal fisiologis tubuh seseorang, sehingga meningkatkan peluang untuk melakukan monitoring secara real time, satu hal yang biasa digunakan adalah sinyal ECG dan PPG.
  - [Stress detection with single PPG sensor by orchestrating multiple denoising and peak-detecting methods](https://ieeexplore.ieee.org/document/9358140/)
  - [Towards an automatic early stress recognition system for office environments based on multimodal measurements](https://linkinghub.elsevier.com/retrieve/pii/S1532046415002750)
  - [Two-stage approach for detection and reduction of motion artifacts in photoplethysmographic data](https://ieeexplore.ieee.org/document/5415601/)
- Stress didefinisikan sebagai aktivasi berlebihan pada sisterm saraf simpatik pada sistem otonom tubuh[Stress management in primary care](https://academic.oup.com/fampra/article-abstract/17/1/98-/507687?redirectedFrom=fulltext)

--- HRV Analysis Background

- HRV digunakan secara luas dan merupakan pengukuran stres fisiologis kuantitatif yang paling akurat. Penelitian sebelumnya telah menggunakan indikator HRV untuk mengenali situasi stres. [Stress and heart rate variability: A meta-analysis and review of the literature.](https://psychiatryinvestigation.org/journal/view.php?doi=10.30773/pi.2017.08.17)
- Namun ada kekurangan dari analisis HRV, dimana HRV membutuhkan banyak alat dan sensor yang membuat pasien tidak nyaman, ditambah lagi asosiasi European Society of Cardiology and the North American Society of Pacing and Electrophysiology menganjurkan sampel 5 menit minimum untuk analisis HRV

  - [Power spectrum analysis of heart rate fluctuation: A quantitative probe of beat-to-beat cardiovascular control](https://www.science.org/doi/10.1126/science.6166045)
  - [Assessment of autonomic function in humans by heart rate spectral analysis](https://pubmed.ncbi.nlm.nih.gov/3970172/)
  - [Power spectral analysis of heart rate and arterial pressure variabilities as a marker of sympatho-vagal interaction in man and conscious dog](https://pubmed.ncbi.nlm.nih.gov/2874900/)

- Sebagai catatan, meskipun PPG dan ECG merupakan hal yang berbeda, penelitian ini menunjukan bahwa PPG dapat digunakan selayaknya ECG dalam HRV analysis. [Evaluation of Mental Stress and Heart Rate Variability Derived from Wrist-based Photoplethysmography](https://ieeexplore.ieee.org/document/8807835)
- Karena banyak studi yang menggunakan sinyal fisiologis sebagai deteksi stress, ditambah kebutuhan akan deteksi real-tim stress meningkat, maka di butuhkanlah asesmen ultra-short-term stress detect[Mental stress assessment using PPG signal a deep neural network approach](https://doi.org/10.1080/03772063.2020.1844068)
- Castaldo menunjukan 6 HRV Features menunjukkan kinerja tinggi dalam klasifikasi stres menggunakan fitur HRV jangka sangat pendek, menunjukkan kemampuan untuk menggunakan fitur HRV yang terdeteksi selama lebih dari satu menit untuk mendeteksi stres mental secara otomatis. [Ultra-short term HRV features as surrogates of short term HRV: a case study on mental stress detection in real life](https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/s12911-019-0742-y)
- Baevsky Stress Index. [Analysis of heart rate variability in space medicine](https://link.springer.com/article/10.1023/A:1014866501535)
- Standard Baseline Filtering 0.5 - 3.0 Hz [Standards of measurement, physiological interpretation, and clinical use, Task Force of TheEuropean Society of Cardiology and The North American Society of Pacing and Electrophysiology](https://onlinelibrary.wiley.com/doi/10.1111/j.1542-474X.1996.tb00275.x)

## Paper 2

---

**Name** : Ultra-short term HRV features as surrogates of short term HRV: a case study on mental stress detection in real life

Recap Article :

- Paper ari R.Castaldo ini menunjukan apakah UST HRV dapat dikatakan valid

Personal Statements:

-
