import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import scipy
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error


DEFAULT_METHODS = ["POS", "LGI", "OMIT", "GREEN", "CHROM"]
DEFAULT_TASKS = ["T1", "T3"]
DEFAULT_SUBJECTS = [
    "s41", "s42", "s43", "s44", "s45", "s46", "s47", "s48",
    "s49", "s50", "s51", "s52", "s53", "s54", "s55", "s56",
]


@dataclass
class ProcessingConfig:
    root_path: str
    output_dir: str
    sample_rate_gt: int = 64
    sample_rate_video: int = 35
    target_duration_seconds: float = 180.0
    rppg_source: str = "auto"


def _zscore(signal: np.ndarray) -> np.ndarray:
    std = np.std(signal)
    if std == 0 or np.isnan(std):
        return np.zeros_like(signal)
    return (signal - np.mean(signal)) / std


def preprocess_ppg(ppg_signal: np.ndarray, fs_ppg: int = 64) -> np.ndarray:
    b, a = scipy.signal.butter(3, [0.7, 2.5], btype="band", fs=fs_ppg)
    ppg_filtered = scipy.signal.filtfilt(b, a, ppg_signal)
    return _zscore(ppg_filtered)


def preprocess_rppg(
    rppg_signal: np.ndarray,
    fs_rppg: int = 35,
    fs_ppg: int = 64,
    target_duration_seconds: float = 180.0,
) -> np.ndarray:
    target_samples = int(target_duration_seconds * fs_ppg)
    samples_to_keep = int(target_duration_seconds * fs_rppg)

    if len(rppg_signal) == 0:
        raise ValueError("rPPG signal is empty")

    if len(rppg_signal) > samples_to_keep:
        rppg_trimmed = rppg_signal[:samples_to_keep]
    else:
        rppg_trimmed = rppg_signal

    if len(rppg_trimmed) < 2:
        raise ValueError("rPPG signal must contain at least 2 samples for interpolation")

    duration_trimmed = len(rppg_trimmed) / fs_rppg
    t_old = np.arange(len(rppg_trimmed)) / fs_rppg
    t_new = np.linspace(0, duration_trimmed, target_samples, endpoint=False)

    cs = scipy.interpolate.CubicSpline(t_old, rppg_trimmed)
    rppg_up = cs(t_new)

    b, a = scipy.signal.butter(3, [0.7, 2.5], btype="band", fs=fs_ppg)
    rppg_filtered = scipy.signal.filtfilt(b, a, rppg_up)
    return _zscore(rppg_filtered)


def compute_metrics(signal: np.ndarray, fs: int, segment_len: int = 25, seg_threshold: float = 0.3):
    peaks, _ = scipy.signal.find_peaks(signal, prominence=0.5)
    if len(peaks) < 2:
        return np.nan, np.nan, np.nan

    rr = np.diff(peaks) / fs
    rr = np.asarray(rr, dtype=float)
    rr = rr[(rr >= 0.3) & (rr <= 2.0)]
    if len(rr) < 2:
        return np.nan, np.nan, np.nan

    clean_rr = []
    num_segments = len(rr) // segment_len
    for i in range(num_segments):
        seg = rr[i * segment_len:(i + 1) * segment_len]
        mean_seg = np.mean(seg)
        lower = mean_seg * (1 - seg_threshold)
        upper = mean_seg * (1 + seg_threshold)
        clean_rr.extend(seg[(seg >= lower) & (seg <= upper)])

    rr_final = np.array(clean_rr)
    if len(rr_final) < 2:
        return np.nan, np.nan, np.nan

    hr = int(60 / np.mean(rr_final))
    rr_ms = rr_final * 1000
    sdnn = int(np.std(rr_ms))
    rmssd = int(np.sqrt(np.mean(np.square(np.diff(rr_ms)))))
    return hr, sdnn, rmssd


def _iter_subject_task_method(subjects: Iterable[str], tasks: Iterable[str], methods: Iterable[str]):
    for subject in subjects:
        for task in tasks:
            yield subject, task, "PPG"
            for method in methods:
                yield subject, task, method


def _rppg_file_candidates(source: str, subject: str, task: str, method: str) -> list[str]:
    detector_patterns = [
        f"{subject}_{task}_{method}_rppg.npy",
        f"{subject}_{task}-{method}-rppg.npy",
    ]
    landmarker_patterns = [
        f"Landmark_{subject}_{task}_{method}_rppg.npy",
        f"Landmark_{subject}_{task}-{method}-rppg.npy",
        f"Optimized_Landmark_{subject}_{task}-{method}-rppg.npy",
        f"Optimized_Landmark_{subject}_{task}_{method}_rppg.npy",
    ]

    if source == "face_detector":
        return detector_patterns
    if source == "face_landmarker":
        return landmarker_patterns

    raise ValueError(f"Unknown rPPG source: {source}")

def _resolve_rppg_path(root_path: str, subject: str, task: str, method: str, source: str) -> Path:
    subject_dir = Path(root_path) / subject
    for candidate in _rppg_file_candidates(source, subject, task, method):
        candidate_path = subject_dir / candidate
        if candidate_path.exists():
            return candidate_path

    searched = ", ".join(_rppg_file_candidates(source, subject, task, method))
    raise FileNotFoundError(
        f"No rPPG file found for subject={subject}, task={task}, method={method}, "
        f"source={source}. Tried: {searched}"
    )


def run_preprocessing(
    config: ProcessingConfig,
    subjects: Iterable[str] = DEFAULT_SUBJECTS,
    tasks: Iterable[str] = DEFAULT_TASKS,
    methods: Iterable[str] = DEFAULT_METHODS,
) -> pd.DataFrame:
    output_dir = Path(config.output_dir)
    preprocessed_dir = output_dir / "preprocessed"
    preprocessed_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for subject, task, method in _iter_subject_task_method(subjects, tasks, methods):
        if method == "PPG":
            raw_path = Path(config.root_path) / subject / f"bvp_{subject}_{task}.csv"
            raw_signal = pd.read_csv(raw_path, header=None).values.flatten()
            preprocessed = preprocess_ppg(raw_signal, fs_ppg=config.sample_rate_gt)
            fs = config.sample_rate_gt
            source_used = "PPG"
        else:
            raw_path = _resolve_rppg_path(
                root_path=config.root_path,
                subject=subject,
                task=task,
                method=method,
                source=config.rppg_source,
            )
            raw_signal = np.load(raw_path)
            preprocessed = preprocess_rppg(
                raw_signal,
                fs_rppg=config.sample_rate_video,
                fs_ppg=config.sample_rate_gt,
                target_duration_seconds=config.target_duration_seconds,
            )
            fs = config.sample_rate_gt
            source_used = config.rppg_source

        file_stem = f"{subject}_{task}_{method}"
        preproc_path = preprocessed_dir / f"{file_stem}.npy"
        np.save(preproc_path, preprocessed)

        records.append(
            {
                "Subject": subject,
                "Task": task,
                "Method": method,
                "RawPath": str(raw_path),
                "PreprocPath": str(preproc_path),
                "RawLen": len(raw_signal),
                "PreprocLen": len(preprocessed),
                "Fs": fs,
                "RPPGSource": source_used,
            }
        )

    manifest = pd.DataFrame(records)
    manifest_path = output_dir / "signal_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    return manifest


def run_metric_extraction(manifest_path: str, output_dir: str) -> pd.DataFrame:
    manifest = pd.read_csv(manifest_path)
    metrics = []

    for _, row in manifest.iterrows():
        signal = np.load(row["PreprocPath"])
        hr, sdnn, rmssd = compute_metrics(signal, int(row["Fs"]))
        metrics.append(
            {
                "Subject": row["Subject"],
                "Task": row["Task"],
                "Method": row["Method"],
                "HR": hr,
                "SDNN": sdnn,
                "RMSSD": rmssd,
            }
        )

    metrics_df = pd.DataFrame(metrics)
    metrics_path = Path(output_dir) / "metrics_long.csv"
    metrics_df.to_csv(metrics_path, index=False)
    return metrics_df


def evaluate_against_gt(metrics_df: pd.DataFrame) -> pd.DataFrame:
    metric_names = ["HR", "SDNN", "RMSSD"]
    methods = ["POS", "GREEN", "LGI", "OMIT", "CHROM"]
    task_to_condition = {"T1": "Rest", "T3": "Task"}

    rows = []
    for metric_name in metric_names:
        for task in ["T1", "T3"]:
            gt = metrics_df[
                (metrics_df["Task"] == task) & (metrics_df["Method"] == "PPG")
            ][["Subject", metric_name]].rename(columns={metric_name: "GT"})

            for method in methods:
                pred = metrics_df[
                    (metrics_df["Task"] == task) & (metrics_df["Method"] == method)
                ][["Subject", metric_name]].rename(columns={metric_name: "Pred"})

                merged = gt.merge(pred, on="Subject", how="inner").dropna()
                if len(merged) < 2:
                    mae, rmse, pc = np.nan, np.nan, np.nan
                else:
                    mae = mean_absolute_error(merged["GT"], merged["Pred"])
                    rmse = np.sqrt(np.mean((merged["GT"] - merged["Pred"]) ** 2))
                    pc, _ = pearsonr(merged["GT"], merged["Pred"])

                rows.append(
                    {
                        "Metric": metric_name,
                        "Condition": task_to_condition[task],
                        "Method": method,
                        "MAE": mae,
                        "RMSE": rmse,
                        "PC": pc,
                    }
                )

    return pd.DataFrame(rows)


def run_all(config: ProcessingConfig) -> None:
    manifest = run_preprocessing(config=config)
    metrics_df = run_metric_extraction(
        manifest_path=str(Path(config.output_dir) / "signal_manifest.csv"),
        output_dir=config.output_dir,
    )
    eval_df = evaluate_against_gt(metrics_df)
    eval_path = Path(config.output_dir) / "evaluation_summary.csv"
    eval_df.to_csv(eval_path, index=False)

    print("Pipeline complete")
    print(f"Manifest: {Path(config.output_dir) / 'signal_manifest.csv'}")
    print(f"Metrics : {Path(config.output_dir) / 'metrics_long.csv'}")
    print(f"Eval    : {eval_path}")


def _parse_args():
    parser = argparse.ArgumentParser(description="Reproducible rPPG processing pipeline")
    parser.add_argument("--root-path", default="dataset_numpy", help="Input dataset folder")
    parser.add_argument("--output-dir", default="artifacts", help="Output folder for generated files")
    parser.add_argument(
        "--rppg-source",
        choices=["face_detector", "face_landmarker"],
        required=True,
        help="Select rPPG input naming convention",
    )
    parser.add_argument("--step", choices=["preprocess", "metrics", "evaluate", "all"], default="all")
    parser.add_argument("--manifest", default="", help="Path to signal_manifest.csv for metrics/evaluate steps")
    parser.add_argument("--metrics", default="", help="Path to metrics_long.csv for evaluate step")
    return parser.parse_args()


def main():
    args = _parse_args()
    config = ProcessingConfig(
        root_path=args.root_path,
        output_dir=args.output_dir,
        rppg_source=args.rppg_source,
    )
    os.makedirs(config.output_dir, exist_ok=True)

    if args.step == "preprocess":
        run_preprocessing(config=config)
        print(f"Saved manifest at {Path(config.output_dir) / 'signal_manifest.csv'}")
        return

    if args.step == "metrics":
        manifest_path = args.manifest or str(Path(config.output_dir) / "signal_manifest.csv")
        run_metric_extraction(manifest_path=manifest_path, output_dir=config.output_dir)
        print(f"Saved metrics at {Path(config.output_dir) / 'metrics_long.csv'}")
        return

    if args.step == "evaluate":
        metrics_path = args.metrics or str(Path(config.output_dir) / "metrics_long.csv")
        metrics_df = pd.read_csv(metrics_path)
        eval_df = evaluate_against_gt(metrics_df)
        eval_path = Path(config.output_dir) / "evaluation_summary.csv"
        eval_df.to_csv(eval_path, index=False)
        print(f"Saved evaluation at {eval_path}")
        return

    run_all(config)


if __name__ == "__main__":
    main()
