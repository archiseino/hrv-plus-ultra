# Evaluating Remote Photoplethysmography Methods on Calculating the Heart Rate and Heart Rate Variability

Language: English | [Bahasa Indonesia](README.id.md)

This repository documents an undergraduate thesis project that evaluates remote photoplethysmography (rPPG) methods against reference PPG signals from UBFC-Phys.

## Project Overview

The study evaluates the quality of several rPPG methods for estimating:

- Heart Rate (HR)
- Heart Rate Variability (HRV) features (SDNN, RMSSD)

Using UBFC-Phys (subjects s41-s56), this study compares multiple rPPG methods and face ROI strategies against contact PPG as the reference signal. The results show that under stationary conditions (T1), several rPPG methods can produce pulse waveforms and HR estimates that track the reference reasonably well, enabling useful HR and selected HRV feature estimation (SDNN, RMSSD). In more active conditions (T2: active, T3: arithmetic), motion from the hand and face introduces stronger artifacts, which degrades waveform quality and reduces agreement with the reference.

The analysis also indicates that ROI choice matters: combining multiple ROI can improve robustness in some cases, but a single well-localized ROI may outperform fragmented ROI combinations depending on scenario and method. Across trials, there is a modest increase in HR during task scenarios, but interpretation should be cautious because part of the change can be explained by motion contamination. Because the dataset does not provide detailed quality annotations for the reference, this work recommends using stronger acquisition modalities (for example ECG) in future studies and adding signal-quality annotations to public datasets to improve evaluation reliability.

## Current Folder Structure

Main folders and files in this workspace:

- `artifacts/`: generated outputs from the processing pipeline
- `dataset_numpy/`: dataset folder (subjects, source files, and method resources)
- `log-bimbingan/`: supervision/progress notes
- `mediapipe_models/`: model files for Face Detector and Face Landmarker
- `pipeline.py`: reproducible processing pipeline (preprocess, metrics, evaluate)
- `rppg-extraction/`: scripts to extract raw rPPG from videos (`face_detector.py`, `face_landmarker.py`)
- `rppg_methods/`: method implementations (CHROM, GREEN, LGI, OMIT, POS)
- `Signalkit/`: proof-of-concept app scripts
- `Signalkit-Export/`: build/export assets and environment files
- `utils/`: analysis notebooks and table outputs

## Environment Setup

### 1. Python Version

- Recommended: Python 3.11
- Minimum: Python 3.10

### 2. Install Dependencies

Run from this folder (`workflow-research`):

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional (PoC app):

```bash
pip install -r Signalkit/requirements.txt
pip install -r Signalkit-Export/requirements.txt
```

### 3. Verify Environment

```bash
python --version
pip --version
python -c "import numpy, scipy, pandas, matplotlib; print('core libs OK')"
```

## Data Preparation

1. Download the UBFC-Phys dataset zip files from the official [source](https://ieee-dataport.org/open-access/ubfc-phys-2).
2. Extract all dataset archives and organize them under `dataset_numpy/`.
3. Ensure subject folders are available from `dataset_numpy/s41` to `dataset_numpy/s56`.

Expected minimal structure:

- `dataset_numpy/s41/`
- `dataset_numpy/s42/`
- ...
- `dataset_numpy/s56/`

At this stage, the folder should contain the extracted source files (for example `.avi`, `.csv`, and metadata files) before rPPG conversion to `.npy`.

## How to Run

Use this execution order:

### Step 1: Extract Dataset Archives

Make sure all UBFC-Phys zip files are extracted first and placed into `dataset_numpy/` as described in Data Preparation.

### Step 2: Generate rPPG `.npy` Files from Video

Run extraction scripts to transform video-based signals into `.npy` files.

```bash
cd rppg-extraction
python face_detector.py
python face_landmarker.py
```

### Step 3: Reproducible Pipeline

The pipeline separates data processing from reporting and creates reusable artifacts.

Face Landmarker source:

```bash
python pipeline.py --root-path dataset_numpy --output-dir artifacts --rppg-source face_landmarker --step all
```

Face Detector source:

```bash
python pipeline.py --root-path dataset_numpy --output-dir artifacts --rppg-source face_detector --step all
```

Generated outputs:

- `artifacts/preprocessed/*.npy`
- `artifacts/signal_manifest.csv`
- `artifacts/metrics_long.csv`
- `artifacts/evaluation_summary.csv`

Run by stage:

```bash
python pipeline.py --root-path dataset_numpy --output-dir artifacts --rppg-source face_landmarker --step preprocess
python pipeline.py --output-dir artifacts --rppg-source face_landmarker --step metrics
python pipeline.py --output-dir artifacts --rppg-source face_landmarker --step evaluate
```

CLI help:

```bash
python pipeline.py --help
```

## Proof-of-Concept App

Primary Signalkit app entry point:

```bash
python Signalkit/v1/main.py
```

Executable (EXE) distribution is provided through this repository's GitHub release assets.

## Reproducibility Notes

- Keep processing results in `artifacts/` for consistent reruns.
- Save an environment snapshot when needed:

```bash
pip freeze > requirements-lock.txt
```

- Record parameter changes in `log-bimbingan/`.

## How to Cite

If you use this repository for academic purposes, cite the thesis:

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

## License

Add license information (for example MIT, Apache-2.0, or institutional license).

## Acknowledgments

- Martin Clinton Manullang, Ph.D.
- Program Studi Teknik Informatika ITERA
- R. Meziati Sabour, Y. Benezeth, P. De Oliveira, J. Chappe, F. Yang. UBFC-Phys: A Multimodal Database For Psychophysiological Studies Of Social Stress, IEEE Transactions on Affective Computing, 2021.
