from pathlib import Path
import sys

import pandas as pd


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR / "models"))

from study_parameters import (
    ANTENNA_HEIGHT_M,
    RECEIVER_HEIGHT_M,
    TRANSMITTER_GROUND_ELEVATION_M,
)

INPUT_DIR = SCRIPTS_DIR / "results" / "line_profiles"
OUTPUT_DIR = SCRIPTS_DIR / "results" / "corrected_profiles"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    arquivos_txt = sorted(INPUT_DIR.glob("*.txt"))

    if not arquivos_txt:
        print(f"Nenhum arquivo TXT encontrado em: {INPUT_DIR}")
        return

    for arquivo in arquivos_txt:
        analisa_txt(arquivo)

    print(f"{len(arquivos_txt)} perfil(is) corrigido(s).")


def analisa_txt(caminho_arquivo: Path) -> None:
    df = pd.read_table(caminho_arquivo, sep=";")
    df.pop("obstrucao")
    df.pop("alt_x")
    df.pop("alt_y")

    altitude = df["altitude (m)"].values.tolist()
    distance_m = df["distance_m"].values.tolist()

    antena = ANTENNA_HEIGHT_M
    cota_tx = TRANSMITTER_GROUND_ELEVATION_M
    soma_cot_tx = antena + cota_tx
    a_rx = RECEIVER_HEIGHT_M
    obstruct = [0] * len(altitude)
    dominant_obstruction_distance_m = [None] * len(altitude)
    max_terrain_slope = float("-inf")
    max_terrain_distance_m = None

    # A target is blocked if a point closer to the transmitter has a steeper angle.
    for i in range(len(altitude) - 2, -1, -1):
        target_slope = (altitude[i] + a_rx - soma_cot_tx) / distance_m[i]
        obstruct[i] = int(max_terrain_slope >= target_slope)
        if obstruct[i]:
            dominant_obstruction_distance_m[i] = max_terrain_distance_m
        terrain_slope = (altitude[i] - soma_cot_tx) / distance_m[i]
        if terrain_slope > max_terrain_slope:
            max_terrain_slope = terrain_slope
            max_terrain_distance_m = distance_m[i]
    df.insert(5, column="obstrucao", value=obstruct, allow_duplicates=True)
    df.insert(6, column="dominant_obstruction_distance_m", value=dominant_obstruction_distance_m, allow_duplicates=True)

    output_path = OUTPUT_DIR / caminho_arquivo.name
    df.to_csv(output_path, sep=";", index=False)


if __name__ == "__main__":
    main()










