from pathlib import Path

import numpy as np
import pandas as pd

from study_parameters import (
    ANTENNA_HEIGHT_M,
    DBI_PER_DBD,
    FREQUENCY_MHZ,
    PROFILE_STEP_M,
    RECEIVER_HEIGHT_M,
    RECEIVER_GAIN_DBI,
    SPEED_OF_LIGHT_M_S,
    TRANSMITTER_GROUND_ELEVATION_M,
    TRANSMITTER_GAIN_DBD,
    TRANSMITTER_POWER_W,
)


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = SCRIPTS_DIR / "results" / "corrected_profiles"
OUTPUT_FILE = SCRIPTS_DIR / "results" / "propagation_models" / "modelo_analitico.txt"


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
    obstruct = df["obstrucao"].values.tolist()
    obstruction_distance_m = df["dominant_obstruction_distance_m"].values.tolist()

    antena = ANTENNA_HEIGHT_M
    cota_tx = TRANSMITTER_GROUND_ELEVATION_M
    soma_cot_tx = antena + cota_tx
    a_rx = RECEIVER_HEIGHT_M
    p_rx = []
    p_tx_watts = TRANSMITTER_POWER_W
    freq_mhz = FREQUENCY_MHZ
    log_freq = np.log10(freq_mhz)
    freq_hz = freq_mhz * 10**6
    c_metro_seg = SPEED_OF_LIGHT_M_S
    lambda1 = c_metro_seg / freq_hz
    n = 16
    h_roof = 3 * n + 3
    delta_hm = h_roof - a_rx
    delta_hb = antena - h_roof
    d = PROFILE_STEP_M

    for i in range(len(altitude) - 1):
        tg_teta = (soma_cot_tx - altitude[i] - a_rx) / distance_m[i]
        x = tg_teta * distance_m[i]
        hipotenusa = np.sqrt(x**2 + distance_m[i] ** 2)

        if obstruct[i] == 0:
            lp = 43.6 + 26 * np.log10(hipotenusa / 1000) + 20 * log_freq
        else:
            l0 = 32.45 + 20 * np.log10(hipotenusa / 1000) + 20 * np.log10(freq_mhz)
            lmsd = 20 * np.log10(2.35 * (delta_hb * 1000 / hipotenusa * np.sqrt(d / lambda1)) ** 0.9)
            lrts = 0
            if not pd.isna(obstruction_distance_m[i]):
                x2 = obstruction_distance_m[i]
                teta = np.arctan(delta_hm / x2)
                r = np.sqrt(delta_hm**2 + x2**2)
                aux = lambda1 / (2 * r * np.pi**2)
                lrts = 20 * np.log10(aux * (1 / teta - 1 / (2 * np.pi + teta)))

            lp = l0 - lrts + lmsd

        prx_dbm = 10 * np.log10(p_tx_watts * 1000) + TRANSMITTER_GAIN_DBD + DBI_PER_DBD + RECEIVER_GAIN_DBI - lp
        p_rx.append(prx_dbm)

    p_rx.append(p_rx[-1])
    df.insert(7, "Modelo Analitico", p_rx)
    return df


if __name__ == "__main__":
    main()










