"""Create a geographic comparison of the experimental propagation models."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(SCRIPTS_DIR / ".matplotlib_cache"))

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


RESULTS_DIR = SCRIPTS_DIR / "results" / "propagation_models"
DEFAULT_OUTPUT = SCRIPTS_DIR / "results" / "coverage_comparison.png"

MODEL_FILES = {
    "Espaco livre": ("espaco_livre.txt", "Espaco Livre"),
    "Lee": ("lee_model.txt", "Lee model"),
    "Okumura-Hata": ("okumura_hata.txt", "Okumura Hata"),
    "Walfisch-Ikegami": ("walfish_ikegami.txt", "Walfish Ikegami"),
    "Modelo analitico": ("modelo_analitico.txt", "Modelo Analitico"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stride", type=int, default=12, help="Keep one of every N samples (default: 12).")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PNG output path.")
    return parser.parse_args()


def load_result(filename: str, value_column: str, stride: int) -> tuple[pd.DataFrame, pd.Series, float]:
    frame = pd.read_csv(RESULTS_DIR / filename, sep=";")
    frame.columns = frame.columns.str.strip()
    columns = ["latitude", "longitude", "altitude (m)", "distance_m", "obstrucao", value_column]
    frame = frame.loc[:, columns].copy()
    transmitter_candidates = frame[frame["distance_m"] == frame["distance_m"].min()]
    transmitter = transmitter_candidates[["latitude", "longitude"]].median()
    max_distance_m = float(frame["distance_m"].max())
    latitude_limit = max_distance_m / 111_320.0 * 1.05
    longitude_limit = latitude_limit / np.cos(np.deg2rad(transmitter["latitude"]))
    in_study_area = (
        frame["latitude"].sub(transmitter["latitude"]).abs() <= latitude_limit
    ) & (
        frame["longitude"].sub(transmitter["longitude"]).abs() <= longitude_limit
    )
    sampled = frame.loc[in_study_area].iloc[::stride].copy()
    sampled.rename(columns={value_column: "power_dbm"}, inplace=True)
    return sampled, transmitter, max_distance_m


def draw_distance_rings(axis: plt.Axes, latitude: float, longitude: float, max_distance_m: float) -> None:
    ring_km = range(10, int(max_distance_m // 1000) + 1, 10)
    angle = np.linspace(0, 2 * np.pi, 241)
    latitude_scale = 111_320.0
    longitude_scale = latitude_scale * np.cos(np.deg2rad(latitude))

    for distance_km in ring_km:
        distance_m = distance_km * 1000
        ring_lat = latitude + distance_m * np.sin(angle) / latitude_scale
        ring_lon = longitude + distance_m * np.cos(angle) / longitude_scale
        axis.plot(ring_lon, ring_lat, color="0.25", linewidth=0.45, alpha=0.45)


def format_axis(axis: plt.Axes, transmitter: pd.Series, max_distance_m: float) -> None:
    draw_distance_rings(axis, transmitter["latitude"], transmitter["longitude"], max_distance_m)
    axis.scatter(
        transmitter["longitude"],
        transmitter["latitude"],
        marker="*",
        s=110,
        color="white",
        edgecolor="black",
        linewidth=0.8,
        label="Transmissor",
        zorder=4,
    )
    axis.set_xlabel("Longitude")
    axis.set_ylabel("Latitude")
    axis.set_aspect(1 / np.cos(np.deg2rad(transmitter["latitude"])))
    axis.grid(alpha=0.15, linewidth=0.4)


def draw_obstructions(axis: plt.Axes, frame: pd.DataFrame) -> None:
    blocked = frame[frame["obstrucao"] == 1]
    axis.scatter(
        blocked["longitude"],
        blocked["latitude"],
        s=1.2,
        marker="x",
        color="black",
        alpha=0.28,
        linewidths=0.25,
        label="Obstruido",
        zorder=3,
    )


def main() -> None:
    args = parse_args()
    if args.stride < 1:
        raise ValueError("--stride deve ser maior ou igual a 1.")

    loaded_models = {
        name: load_result(filename, column, args.stride)
        for name, (filename, column) in MODEL_FILES.items()
    }
    models = {name: result[0] for name, result in loaded_models.items()}
    reference = next(iter(models.values()))
    transmitter = next(iter(loaded_models.values()))[1]
    max_distance_m = next(iter(loaded_models.values()))[2]

    signal_values = np.concatenate([frame["power_dbm"].to_numpy() for frame in models.values()])
    signal_min, signal_max = np.quantile(signal_values, [0.01, 0.99])

    figure, axes = plt.subplots(2, 3, figsize=(17, 11), constrained_layout=True)
    elevation_axis = axes.flat[0]
    elevation = elevation_axis.scatter(
        reference["longitude"],
        reference["latitude"],
        c=reference["altitude (m)"],
        cmap="terrain",
        s=2.0,
        alpha=0.8,
        linewidths=0,
    )
    draw_obstructions(elevation_axis, reference)
    format_axis(elevation_axis, transmitter, max_distance_m)
    elevation_axis.set_title("Relevo e obstrucoes")
    elevation_axis.legend(loc="lower left", fontsize=8)
    figure.colorbar(elevation, ax=elevation_axis, label="Elevacao (m)")

    signal_plot = None
    for axis, (name, frame) in zip(axes.flat[1:], models.items()):
        signal_plot = axis.scatter(
            frame["longitude"],
            frame["latitude"],
            c=frame["power_dbm"],
            cmap="turbo",
            vmin=signal_min,
            vmax=signal_max,
            s=2.0,
            alpha=0.82,
            linewidths=0,
        )
        draw_obstructions(axis, frame)
        format_axis(axis, transmitter, max_distance_m)
        axis.set_title(name)

    figure.colorbar(signal_plot, ax=axes.flat[1:], label="Potencia recebida prevista (dBm)")
    figure.suptitle("Comparacao espacial dos modelos de propagacao", fontsize=16)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180, bbox_inches="tight")
    print(f"Visualizacao salva em: {args.output}")


if __name__ == "__main__":
    main()
