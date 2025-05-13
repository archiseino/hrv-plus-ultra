## Hi...

- Based on the Article, it seems any paper that doing this is based on the sample signals over 5 min (Long term)
- Because of reason above, one needs to use the UST (Ultra Short Term) HRV analysis, but it's only for looking the correlation between the trend of the short one and the standard one.
- For detecting stress itself, one should define a rule for the case, since many doesn't defy anything for stress.
- ML Models? Nah we don't have many data.
- Evaluation? we can use the Bland-Altman and Pearson Correlation for commparing the short and standard one, and MAE, MSAE for comparing the original GT and PPG GT
- Does using neurokit2, pyvhr apakah valid untuk asesmen ini, atau bahkan menggunakan software 3rd party seperti KubiosHRV

# Notes on the Paper Article

Collection of Recap Article for TA Purpose

---

## Paper 0

---

**Name** : A Critical Review of Ultra-Short-Term Heart Rate Variability Norms Research

Paper explanation: [ref](https://chatgpt.com/share/68077ff9-b718-8007-babe-cc48caca47b8)

Recap Article :

- The conclusion emphasizes that correlation and regression do not equate to agreement and should not be used as primary tools in method-comparison studies. Instead, Bland–Altman LoA with confidence intervals is recommended to assess agreement between short-duration and 300-s RMSSD measures. The authors suggest a practical workflow that begins with checking for normality, defining acceptable differences a priori, conducting Bland–Altman plots and equality testing, and incrementally identifying the shortest acceptable surrogate duration.

#### Key Points of the Paper:

1. Method Comparison in UST-HRV Analysis:

- Correlation/Regression Analyses are often misused as they don’t assess agreement, only association. This is a major issue when comparing different methods of measuring HRV.
- The Bland-Altman plot (LoA) is a better alternative for assessing whether two methods of measuring HRV agree. It helps visualize differences between methods and identify biases or outliers.

2. Misuse of Traditional Statistical Tests:

- Studies often incorrectly rely on mean/median differences (e.g., t-tests or Kruskal-Wallis) to claim comparability between methods. This is problematic as non-significant differences could arise due to underpowered studies or the methods not measuring the same underlying phenomenon.

- Simple regression or the coefficient of determination (r²) also fail to properly account for agreement because they don't consider the measurement errors in both methods being compared.

3. The Right Way: Limits of Agreement (LoA):

- LoA in Bland-Altman plots is the recommended method for assessing agreement between UST and short-term HRV measurements (e.g., RMSSD). This method compares the difference between the two methods and shows whether the differences fall within an acceptable range.

- Researchers need to decide a priori what the acceptable difference is for agreement between methods before conducting the analysis.

4. Practical Workflow for Comparing Short-Duration vs. 300-s RMSSD:

- Step-by-step guidelines for using Bland-Altman analysis with log transformation for non-normally distributed data.

- The workflow includes checking normality, setting an acceptable margin of difference, and performing a Student’s t-test to confirm whether shorter-duration HRV measures can serve as surrogates for the 5-minute baseline.

5. Importance of Confidence Intervals:

- Confidence intervals (95% CI) are essential in Bland-Altman plots to capture the variability in the differences and ensure proper statistical validation.

6. Incorporation of Outlier Detection:

- Outliers can be detected via Bland-Altman plots, which adds another layer of insight into the comparability of the methods.

7. Conclusion on Recommendations:

- LoA analysis should be the primary tool in method comparison studies. Correlation/regression analyses are less helpful and often misunderstood in this context.

- The paper suggests conducting a method comparison study focusing on agreement, not just association, and provides a structured approach for doing so.

#### 🧠 Important Points NOT Covered (but should be considered):

🥇 1. Baseline vs. Stressor Conditions in HRV Estimation
Why it's important:

- HRV is highly state-dependent. RMSSD during a calm, seated baseline will behave differently than RMSSD during or after a stressor (e.g., exercise, emotional stress).

- Short-term HRV (e.g., 30s or 60s) is more vulnerable to transient fluctuations and may not reflect true autonomic tone during high variability states.

Why the paper misses the mark:

- It assumes that if a 30s measurement aligns with a 300s one statistically, then it’s a valid surrogate.

- But this assumes stationarity, i.e., that the HRV signal doesn't vary across that time — which is often untrue during stress or recovery.

- No mention is made of validating agreement across physiological states, which can dramatically affect results.

Implication:

- A short window that "agrees" with 300s in baseline may fail completely under stress, making it an unreliable general surrogate.

✅ For Point 2: Absence of Gold Standard (300s RMSSD)

- Frame the other successful other UST analysis.

```
"While our dataset lacks standard 5-minute HRV segments typically used as gold-standard references, prior research has shown that ultra-short-term HRV features (e.g., RMSSD from 30s or 60s windows) can serve as valid surrogates under specific conditions (Shaffer & Ginsberg, 2017; Esco & Flatt, 2014). Thus, we interpret our findings within this established framework, acknowledging that full agreement with 5-minute standards cannot be empirically verified in this study."
```

#### 🧠 Citations You Can Use as Backups

Here are some commonly cited sources that validate UST-HRV features:

1. Shaffer & Ginsberg, 2017 – An Overview of HRV Metrics and Norms

- Frequently cited for summarizing valid durations and contexts for UST RMSSD.
- States that 30s RMSSD is often acceptable for tracking autonomic changes, especially in athletic and field settings.

2. Esco & Flatt, 2014 – Ultra-Short-Term HRV in Athletes

- Validates RMSSD and HR from 1-minute recordings as surrogates for 5-minute recordings in well-controlled conditions.

3. Munoz et al., 2015 – Validity of Short-Term HRV Analysis Using a New Method

- Explores HRV durations from 10s to 300s, shows good agreement for 60s+ durations depending on the feature and context.

4. Baek et al., 2015 – Reliability of Short-Duration HRV Analysis Using 10-Second ECGs

- Even 10s HRV has acceptable reliability for time-domain metrics like RMSSD, but with reduced sensitivity.

5. Castaldo et al., 2019 – Ultra-Short HRV Features as Surrogates of Standard HRV in Stress Detection
   - Compares UST features under stressor vs. baseline conditions and reports good classification performance using 10s–30s RMSSD.

Personal Statements:

- Paper ini bisa menjadi acuan dalam membuat deteksi stress menggunakan HRV sebagai panduan / pipeline penelitian.

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

- Paper ari R.Castaldo ini menunjukan apakah UST HRV dapat dikatakan valid sebagai pengganti yang sah untuk HRV pendek (minimal 5 menit).
- Metode yang digunakan pada kasus ini ada 42 subject dan hrv diextract dengan berbagai rentang. Ada dua jenis metode pengambilan data, ketika ujian yang disebut dengan stressor dan ketika istirahat setelah ujian (disebut dengan rest)
- Metode evlauasi dari UST di compare dengan short HRV feature melalui spearman rank correlation dan plot bland-altman pada test rest dan stress phase (Label test untuk model ML)

Personal Statements:

- Menurutku, paper ini juga bisa menjadi ground statements untuk TA, karena kita bisa melakukan komparasi hrv features pada menit 1 dan 3 dan melihat polanya serta trendnya.
- Untuk label sendiri, sama seperti paper 1 dimana ada dua test yang digunakan untuk label rest dan stressor.

Reference other paper that still relevant.

- Stres didefinisikan sebagai pola respons spesifik dan nonspesifik yang dibuat organisme terhadap peristiwa stimulus yang mengganggu keseimbangannya dan membebani atau melebihi kemampuannya untuk mengatasinya [American Psychological Association: Glossary of Psychological Terms: Pearson Education, Education, Incorporated](https://dictionary.apa.org/)
- Stress mempengaruhi pengambilan keputusan dan telah ditunjukan juga mengurangi performa seseorang ketika main game. [Heart rate variability analysis and performance during a repeated mental workload task](https://www.researchgate.net/publication/317624571_Heart_Rate_Variability_Analysis_and_Performance_During_A_Repeated_Mental_Workload_Task)
- Hasil evaluasi nilai MeanNN, StdNN, MeanHR, StdHR, HF
  and SD2 dapat digunakan sebagai estimasi untuk short HRV features karena mempunyai trends yang sama dengan 5 menit.

-- HRV

- HRV menggambarkan variasi interval antara puncak gelombang R yang berurutan dalam EKG dan dapat dianalisis dalam domain waktu, frekuensi, dan non-linier. Analisis HRV dapat dilakukan pada rekaman nominal 24 jam (didefinisikan sebagai analisis HRV jangka panjang), rekaman 5 menit (didefinisikan sebagai analisis HRV jangka pendek) atau rekaman yang lebih pendek. [Force T. Heart rate variability guidelines: standards of measurement,physiological interpretation, and clinica](https://www.researchgate.net/publication/279548912_Heart_rate_variability_Standards_of_measurement_physiological_interpretation_and_clinical_use)
- Bagaimanapun, masih sedikit penelitian dalam bidang real-life / real-tme stress detection menggunakan UST-HRV, demands dari pengeakan stress juga real-time juga meningkat seiring bertambahnya penggunaan wearables.

  - [Biosignal monitoring using wearables: observations and opportunities. Biomedical Signal Processing and Control](https://www.sciencedirect.com/science/article/abs/pii/S1746809417300617)
  - [Are ultra-short heart rate variability features good surrogates of short term ones? Literature review and method recommendations](https://pubmed.ncbi.nlm.nih.gov/29922478/)

- Paper ini yang menjelaskan / investigasi dari validasi UST-HRV features secara rinci [Validity of (ultra-) short recordings for heart rate variability measurements.](https://pubmed.ncbi.nlm.nih.gov/26414314/)
- In general, HRV features resulted less correlated in resting than during stress conditions. This is most likely due to the fact that HRV showed a more depressed dynamic during stress phase. Similar behaviors have been observed in other studies

## Paper 3

---

**Name** : Mental Stress Assessment Using Ultra Short Term HRV Analysis Based on Non-Linear Method

Recap Article :

- Paper dari Seungjae Lee menunjukan asesmen stress menggunakan metode non-linear karena menggunakan Ultra Short Term (UST) HRV.
- Karena sinyal HRV itu non-linear dan non-stasioner, karena kompleksitas dari sistem jantung. Paper ini menggunkana Empirical Methods Decomposition. metode sinyal domain waktu-frekuensi dengan karakteristik non-stasioner dan non-linier
- Dataset yang digunakan sendiri menggunakan PhysioNet yang mengasumsikan subjek sedang stress dalam stress test untuk memudahkan proses klasifikasi, ditambah dataset sendiri.
- Metode HRV analisis sendiri menggunakan IMF (Intrinsic Mode Function) yang diambil dari EMD yang bisa memberikan nilai proxy dari freq. domains yang menggunakan data kurang dari 5 menit untuk HRV analysis.
- Sebagai perbandingan dengan HRV jangka sangat pendek, kami menganalisis HRV jangka pendek menggunakan data yang dikumpulkan selama 5 menit, yang merupakan panjang data yang umum digunakan dalam penelitian sebelumnya. Kami memilih kondisi istirahat dan kondisi stres untuk setiap peserta menggunakan peringkat intensitas stres subjektif
- Metode evaluasi yang digunakan sendiri yakni, membandingkan relasi features dari freq domains dengan IMF energy features, Hasil dari Pearson correlation menunjukan bahwa IMF energy features dapat digunakan sebagai pengganti dari freq domains features.
- ini adalah studi pertama yang menunjukkan bahwa fitur domain frekuensi seperti HF, LF, dan rasio dapat digantikan dengan fitur HRV lainnya

Personal Statements:

- Paper ini cukup bagus, kita bisa menggunakan IMF sebagai proxy dari freq domain analysis, yang dimana bakal cukup membantu buat real-time detection.
- Kupikir, judulnya membahas tentang non-linear features, tapi berfokus pada pengganti freq. domains

Reference for TA.

- Stres mental sebagian besar diklasifikasikan menjadi stres kronis dan stres akut. Ketika seseorang menghadapi stresor akut, tubuh manusia memicu respons "lawan atau lari", mekanisme bertahan hidup yang dipicu oleh rangsangan eksternal untuk mempertahankan homeostasis. Respons ini mengaktifkan sistem saraf simpatik dalam sistem saraf otonom (ANS) tubuh dan menyebabkan perubahan dalam tubuh melalui sistem endokrin.[Anxiety, Reactivity, and Social Stress-Induced Cortisol Elevation in Humans](http://www.ncbi.nlm.nih.gov/pubmed/16136010)
- Metode yang dijelaskan dengan baik untuk menginduksi stres akut pada manusia meliputi tes kata warna Stroop [19], Tes Stres Sosial Trier (TSST) [20], tugas aritmatika mental [21], berbicara di depan umum [22], Tugas Stres Pencitraan Montreal [23], dan menonton film horor [24]. Menurut tinjauan stres akut [25]

  - [ Analysis of Stroop Colorword Test-Based Human Stress Detection Using Electrocardiography and Heart Rate Variability Signals](http://doi.org/10.1007/s13369-013-0786-8)
  - [. The ‘Trier Social Stress Test’—A Tool for Investigating Psychobiological Stress Responses in a Laboratory Setting](http://doi.org/10.1159/000119004)
  - [Machine Learning Framework for the Detection of Mental Stress at Multiple Level](http://doi.org/10.1109/ACCESS.2017.2723622)
  - [W. Stress Measurement Using Speech: Recent Advancements, Validation Issues, and Ethical and Privacy Considerations.](http://doi.org/10.1080/10253890.2019.1584180)
  - [ A Study about Feature Extraction for Stress Detection](http://doi.org/10.1109/ATEE.2013.6563421)
  - [An Electrocardiogram Acquisition and Analysis System for Detection of Human Stress.](http://doi.org/10.1109/CISP-BMEI48845.2019.8965708)

- Studi-studi ini menggunakan fitur-fitur HRV yang terkait dengan ANS. Karena analisis HRV jangka pendek dan jangka sangat pendek memiliki panjang data yang berbeda, maka fitur-fitur HRV jangka sangat pendek perlu divalidasi sebagai fitur-fitur jangka pendek. Di antara fitur-fitur HRV yang terkait dengan stres, fitur-fitur domain frekuensi sangat dipengaruhi oleh panjang data. Untuk mengukur daya spektrum frekuensi tinggi (HF) dan frekuensi rendah (LF), data HRV diperlukan untuk durasi masing-masing minimal 60 dan 250 detik. [Force, T. Heart Rate Variability Guidelines: Standards of Measurement, Physiological Interpretation, and Clinica Use](https://pubmed.ncbi.nlm.nih.gov/8598068/)

- Since the HRV signal is non-linear and non-stationary due to the dynamics of the complex cardiac system, it is appropriate to use Empirical Mode Decomposition (EMD), a time-frequency domain signal method with non-stationary and non-linear characteristics. There are studies that have conducted stress analysis of HRV signals using the EMD method
  - [Psychological Stress Detection Using Phonocardiography Signal: An Empirical Mode Decomposition Approach.](http://doi.org/10.1016/j.bspc.2018.12.028)
  - [An Application of Phonocardiography Signals for Psychological Stress Detection Using Non-Linear Entropy Based Features in Empirical Mode Decomposition Domain](http://doi.org/10.1016/j.asoc.2019.01.006)
  - [Characterization of Heart Rate Variability Signal for Distinction of Meditative and Pre-Meditative States](http://doi.org/10.1016/j.bspc.2021.102414)

## Paper 4

---

**Name** : Driver Stress Detection Using Ultra-Short-Term HRV Analysis under Real World Driving Conditions

Recap Article :

- Alur penelitian yang dilakukan di paper ini yakni melakukan test statistik terhadap UST dan ST HRV apakah cocok untuk mendeteksi stress pada pengemudi, lalu dilakukan pembuatan ML model.
- The RR intervals were extracted from the ECG signals using the PhysioNet HRV toolkit, a rigorously validated open-source software package for HRV analysis.
- Hasil kami menunjukkan bahwa **MeanNN, SDNN, NN20, dan MeanHR** dapat digunakan untuk
  menggantikan fitur HRV jangka pendek yang sesuai untuk mendeteksi tingkat stres pengemudi.

Personal Statements:

- Menurutku ini sudah bisa menjadi contoh buat pembanding di Bab 2

## Paper 5

---

**Name** : An optimization study of the ultra-short period for HRV analysis at rest and post-exercise

Recap Article :

- Paper ini bertujuan untuk mencari tahu relasi dari UST dan Standard 5 Min HRV dalam kondisi istirahat dan post-exercise.
- Metode penelitian yang digunakan, 69 partisipan direkrut untuk melakukan tes fisik pada treadmil dengan intensitas, 6 Km/h, 9 Km/h dan 12 Km/h.
- The normal-to-normal RR intervals corresponding to sinus rhythm were automatically downloaded and subsequently exported to Kubios HRV software for further analysis. [Kubios HRV – Heart rate variability analysis software](https://www.sciencedirect.com/science/article/abs/pii/S0169260713002599)
- ANOVA with repeated-measures and Cohen's d statistics were conducted, and Bland-Altman analysis and interclass correlation coefficients (ICC) were used to assess the levels of agreement.
- Specifically, ultra-shortterm HRV0–30s or HRV0-1min was recommended at rest condition, whereas longer than 2 min recording period was reliable to obtain SDNN and RMSSD for the accuracy of HRV analysis.

Personal Statements:

- This is also good Reference for TA

Reference other paper that still relevant.

- Based on the present findings, the enhancement of parasympathetic activity and sympathetic withdrawal could be concluded during the recovery period of exercise by using ultra-short-term HRV analysis, which was in agreement with previous studies.
  - [Heart rate response and parasympathetic modulation during recovery from exercise in boys and men](https://cdnsciencepub.com/doi/10.1139/apnm-2013-0510)
  - [Heart Rate Variability During Acute Recovery from Maximal Exercise; Utility of a Nonlinear Dynamics Approach](https://journals.lww.com/acsm-msse/fulltext/2017/05001/heart_rate_variability_during_acute_recovery_from.2109.aspx)
