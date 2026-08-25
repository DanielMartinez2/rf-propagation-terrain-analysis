from pathlib import Path

import numpy as np
import pandas as pd

from study_parameters import (
    ANTENNA_HEIGHT_M,
    DBI_PER_DBD,
    FREQUENCY_MHZ,
    LEE_DISTANCE_SLOPE_DB_PER_DECADE,
    LEE_FREQUENCY_CORRECTION,
    LEE_REFERENCE_FREQUENCY_MHZ,
    LEE_REFERENCE_RECEIVED_POWER_DBM,
    RECEIVER_GAIN_DBI,
    RECEIVER_HEIGHT_M,
    TRANSMITTER_GAIN_DBD,
    TRANSMITTER_GROUND_ELEVATION_M,
    TRANSMITTER_POWER_W,
)


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = SCRIPTS_DIR / "results" / "corrected_profiles"
OUTPUT_FILE = SCRIPTS_DIR / "results" / "propagation_models" / "lee_model.txt"


def salvar_dataframe(df: pd.DataFrame, output_path: Path) -> Path:
    try:
        df.to_csv(output_path, sep=";", index=False)
        return output_path
    except PermissionError:
        fallback_path = output_path.with_name(f"{output_path.stem}_generated{output_path.suffix}")
        df.to_csv(fallback_path, sep=";", index=False)
        return fallback_path


def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    arquivos = sorted(INPUT_DIR.glob("*.txt"))
    if not arquivos:
        print(f"Nenhum perfil corrigido encontrado em: {INPUT_DIR}")
        return

    dataframes = [analisa_txt(arquivo) for arquivo in arquivos]
    output_path = salvar_dataframe(pd.concat(dataframes, sort=False), OUTPUT_FILE)
    print(f"Resultado salvo em: {output_path}")


def analisa_txt(caminho_arquivo: Path) -> pd.DataFrame:
    df = pd.read_table(caminho_arquivo, sep=";")
    df.columns = df.columns.str.strip()

    altitude = df["altitude (m)"].values.tolist()
    distance_m = df["distance_m"].values.tolist()
    antena = ANTENNA_HEIGHT_M
    cota_tx = TRANSMITTER_GROUND_ELEVATION_M
    soma_cot_tx = antena + cota_tx
    a_rx = RECEIVER_HEIGHT_M
    p_rx = []
    p_tx_watts = TRANSMITTER_POWER_W
    g_rx_dbi = RECEIVER_GAIN_DBI
    g_rx_dbd = g_rx_dbi - DBI_PER_DBD
    g_tx_dbd = TRANSMITTER_GAIN_DBD
    freq_mhz = FREQUENCY_MHZ
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
        pr = (
            LEE_REFERENCE_RECEIVED_POWER_DBM
            - LEE_DISTANCE_SLOPE_DB_PER_DECADE * np.log10(hipotenusa / 1000)
            - LEE_FREQUENCY_CORRECTION * np.log10(freq_mhz / LEE_REFERENCE_FREQUENCY_MHZ)
            + a0
        )
        p_rx.append(pr)

    p_rx.append(p_rx[-1])
    df.insert(7, "Lee model", p_rx)
    return df


if __name__ == "__main__":
    main()










