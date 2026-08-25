from pathlib import Path
import sys

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT_DIR / "scripts"))

from models.study_parameters import ANTENNA_HEIGHT_M, TRANSMITTER_GROUND_ELEVATION_M

INPUT_DIR = ROOT_DIR / "data" / "intermediate" / "gpx_txt_converted"
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "line_profiles"
TARGET_LENGTH = 2333
TOTAL_DISTANCE_M = 69960
STEP_M = 30


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
    df = pd.read_table(caminho_arquivo, sep="\t")
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
    a_rx = 1.0
    alt_x = []
    alt_y = []
    obstruct = []
    true_distance = list(range(TOTAL_DISTANCE_M, -1, -STEP_M))

    if soma_cot_tx > altitude[0]:
        for i in range(len(altitude)):
            x = (soma_cot_tx - a_rx - altitude[0]) * true_distance[i] / true_distance[0]
            y = x + altitude[0] + a_rx
            alt_x.append(x)
            alt_y.append(y)
            obstruct.append(1 if altitude[i] > y else 0)
    else:
        for i in range(len(altitude)):
            x = (altitude[0] + a_rx - soma_cot_tx) * true_distance[i] / true_distance[0]
            y = soma_cot_tx + x - a_rx
            alt_x.append(x)
            alt_y.append(y)
            obstruct.append(0)

    df.insert(3, column="distance_m", value=true_distance, allow_duplicates=True)
    df.insert(4, column="alt_x", value=alt_x, allow_duplicates=True)
    df.insert(5, column="alt_y", value=alt_y, allow_duplicates=True)
    df.insert(7, column="obstrucao", value=obstruct, allow_duplicates=True)

    output_path = OUTPUT_DIR / f"{name[0]}.txt"
    df.to_csv(output_path, sep=";", index=False)


if __name__ == "__main__":
    main()










