from pathlib import Path

import numpy as np
import pandas as pd

from study_parameters import (
    ANTENNA_HEIGHT_M,
    FREQUENCY_MHZ,
    RECEIVER_GAIN_DBI,
    RECEIVER_HEIGHT_M,
    TRANSMITTER_GAIN_DBD,
    TRANSMITTER_GROUND_ELEVATION_M,
    TRANSMITTER_POWER_W,
)


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "data" / "processed" / "corrected_profiles"
OUTPUT_FILE = ROOT_DIR / "results" / "propagation_models" / "lee_model.txt"


def salvar_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    try:
        df.to_csv(output_path, sep=";", index=False)
        return output_path
    except PermissionError:
        fallback_path = output_path.with_name(f"{output_path.stem}_generated{output_path.suffix}")
        df.to_csv(fallback_path, sep=";", index=False)
        return fallback_path


def main() -> None:
    arquivos = sorted(INPUT_DIR.glob("*.txt"))
    if not arquivos:
        print(f"Nenhum perfil corrigido encontrado em: {INPUT_DIR}")
        return

    dataframes = [analisa_txt(arquivo) for arquivo in arquivos]
    output_path = salvar_dataframe(pd.concat(dataframes, sort=False), OUTPUT_FILE)
    print(f"Resultado salvo em: {output_path}")


def analisa_txt(caminho_arquivo: Path) -> pd.DataFrame:
    df = pd.read_table(caminho_arquivo, sep=";")

    altitude = df["altitude (m)"].values.tolist()
    distance_m = df["distance_m"].values.tolist()
    antena = ANTENNA_HEIGHT_M
    cota_tx = TRANSMITTER_GROUND_ELEVATION_M
    soma_cot_tx = antena + cota_tx
    a_rx = RECEIVER_HEIGHT_M
    p_rx = []
    p_tx_watts = TRANSMITTER_POWER_W
    g_rx_dbi = RECEIVER_GAIN_DBI
    g_rx_dbd = g_rx_dbi - 2.5
    g_tx_dbd = TRANSMITTER_GAIN_DBD
    freq_mhz = FREQUENCY_MHZ
    n = 3
    f0 = 900
    a0 = (
        20 * np.log10(antena / 30.48)
        + 10 * np.log10(p_tx_watts / 10)
        + g_rx_dbd
        - 6
        + g_tx_dbd
        + 10 * np.log10(a_rx / 3.048)
    )

    for i in range(len(altitude) - 1):
        tg_teta = (soma_cot_tx - altitude[i] - a_rx) / distance_m[i]
        x = tg_teta * distance_m[i]
        hipotenusa = np.sqrt(x**2 + distance_m[i] ** 2)
        pr = -70 - 36.8 * np.log10(hipotenusa / 1000) - n * np.log10(freq_mhz / f0) + a0
        p_rx.append(pr)

    p_rx.append(p_rx[-1])
    df.insert(7, "Lee model", p_rx)
    return df


if __name__ == "__main__":
    main()










