from pathlib import Path
import csv
import sys

import pandas as pd


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR / "models"))

from study_parameters import (
    ANTENNA_HEIGHT_M,
    PROFILE_STEP_M,
    PROFILE_TOTAL_DISTANCE_M,
    RECEIVER_HEIGHT_M,
    TRANSMITTER_GROUND_ELEVATION_M,
)

INPUT_DIR = PROJECT_ROOT / "data" / "intermediate" / "gpx_txt_converted"
OUTPUT_DIR = SCRIPTS_DIR / "results" / "line_profiles"
TARGET_LENGTH = 2333


def read_intermediate_profile(caminho_arquivo: Path) -> pd.DataFrame:
    """Read GPX-derived TSV files while repairing known empty-field artifacts."""
    with caminho_arquivo.open(encoding="utf-8", newline="") as source:
        reader = csv.reader(source, delimiter="\t")
        header = [column.strip() for column in next(reader)]
        rows = []

        for line_number, row in enumerate(reader, start=2):
            values = [value.strip() for value in row]
            if len(values) == len(header) + 1 and values[5] == "":
                del values[5]
            elif len(values) == len(header) + 1 and values[2] == "":
                del values[2]

            if len(values) != len(header):
                raise ValueError(f"Esquema invalido em {caminho_arquivo.name}, linha {line_number}.")
            if values[4] == "":
                values[4] = "0"
            rows.append(values)

    df = pd.DataFrame(rows, columns=header)
    for column in ["latitude", "longitude", "altitude (m)", "distance (km)", "angle"]:
        df[column] = pd.to_numeric(df[column], errors="raise")

    valid_coordinates = df["latitude"].between(-90, 90).all() and df["longitude"].between(-180, 180).all()
    valid_distances = (df["distance (km)"] >= 0).all()
    if not valid_coordinates or not valid_distances:
        raise ValueError(f"Coordenadas ou distancias invalidas em {caminho_arquivo.name}.")

    df["name"] = df["name"].str.strip()
    return df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    arquivos_txt = sorted(INPUT_DIR.glob("*.txt"))

    if not arquivos_txt:
        print(f"Nenhum arquivo TXT encontrado em: {INPUT_DIR}")
        return

    for arquivo in arquivos_txt:
        analisa_txt(arquivo)

    print(f"{len(arquivos_txt)} perfil(is) processado(s).")


def analisa_txt(caminho_arquivo: Path) -> None:
    df = read_intermediate_profile(caminho_arquivo)
    keys = df.keys().tolist()
    angle_key = keys[-1]

    df.drop("desc", inplace=True, axis=1, errors="ignore")
    df.drop("distance (km)", inplace=True, axis=1, errors="ignore")
    df.drop("type", inplace=True, axis=1, errors="ignore")

    angle = df[angle_key].values.tolist()
    name = df["name"].values.tolist()
    altitude = df["altitude (m)"].values.tolist()

    if len(altitude) == TARGET_LENGTH - 1:
        new_row = pd.Series(
            {
                "latitude": -23.559528028,
                "longitude": -46.656664688,
                "altitude (m)": 825.2,
                "name": name[0],
                f"{angle_key}": angle[0],
            }
        )
        df = pd.concat([df, new_row.to_frame().T], ignore_index=True)

    if len(altitude) > TARGET_LENGTH:
        df = df.iloc[:TARGET_LENGTH].copy()

    angle = df[angle_key].values.tolist()
    name = df["name"].values.tolist()
    altitude = df["altitude (m)"].values.tolist()

    antena = ANTENNA_HEIGHT_M
    cota_tx = TRANSMITTER_GROUND_ELEVATION_M
    soma_cot_tx = antena + cota_tx
    a_rx = RECEIVER_HEIGHT_M
    alt_x = []
    alt_y = []
    obstruct = []
    true_distance = list(range(PROFILE_TOTAL_DISTANCE_M, -1, -PROFILE_STEP_M))
    receiver_height = altitude[0] + a_rx

    # distance_m is measured from the transmitter: 0 m at its site and D at the receiver.
    for i, distance_m in enumerate(true_distance):
        line_height = soma_cot_tx + (receiver_height - soma_cot_tx) * distance_m / PROFILE_TOTAL_DISTANCE_M
        alt_x.append(line_height - altitude[i] - a_rx)
        alt_y.append(line_height)
        obstruct.append(1 if altitude[i] > line_height else 0)

    df.insert(3, column="distance_m", value=true_distance, allow_duplicates=True)
    df.insert(4, column="alt_x", value=alt_x, allow_duplicates=True)
    df.insert(5, column="alt_y", value=alt_y, allow_duplicates=True)
    df.insert(7, column="obstrucao", value=obstruct, allow_duplicates=True)

    output_path = OUTPUT_DIR / f"{name[0].strip()}.txt"
    df.to_csv(output_path, sep=";", index=False)


if __name__ == "__main__":
    main()










