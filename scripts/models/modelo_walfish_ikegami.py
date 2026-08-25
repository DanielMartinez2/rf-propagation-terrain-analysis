from pathlib import Path

import numpy as np
import pandas as pd

from study_parameters import (
    ANTENNA_HEIGHT_M,
    DBI_PER_DBD,
    FREQUENCY_MHZ,
    RECEIVER_HEIGHT_M,
    RECEIVER_GAIN_DBI,
    SPEED_OF_LIGHT_M_S,
    TRANSMITTER_GROUND_ELEVATION_M,
    TRANSMITTER_GAIN_DBD,
    TRANSMITTER_POWER_W,
)


SCRIPTS_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = SCRIPTS_DIR / "results" / "corrected_profiles"
OUTPUT_FILE = SCRIPTS_DIR / "results" / "propagation_models" / "walfish_ikegami.txt"


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
    b = 35
    w = b / 2
    fi = 90
    n = 16
    h_roof = 3 * n + 3
    l_ori = 4.0 - 0.114 * (fi - 55)
    delta_hm = h_roof - a_rx
    delta_hb = antena - h_roof
    ka = 54
    kd = 18
    kf = -4 + 1.5 * (freq_mhz / 925 - 1)

    for i in range(len(altitude) - 1):
        tg_teta = (soma_cot_tx - altitude[i] - a_rx) / distance_m[i]
        x = tg_teta * distance_m[i]
        hipotenusa = np.sqrt(x**2 + distance_m[i] ** 2)

        if obstruct[i] == 0:
            lp = 43.6 + 26 * np.log10(hipotenusa / 1000) + 20 * log_freq
        else:
            l0 = 32.45 + 20 * np.log10(hipotenusa / 1000) + 20 * np.log10(freq_mhz)
            l_rts = -16.9 - 10 * np.log10(w) + 10 * log_freq + 20 * np.log10(delta_hm) + l_ori
            lbsh = -18 * np.log10(1 + delta_hb)
            l_msd = lbsh + ka + kd * np.log10(hipotenusa / 1000) + kf * log_freq - 9 * np.log10(b)
            lp = l0 + l_rts + l_msd if l_rts + l_msd >= 0 else l0

        prx_dbm = 10 * np.log10(p_tx_watts * 1000) + TRANSMITTER_GAIN_DBD + DBI_PER_DBD + RECEIVER_GAIN_DBI - lp
        p_rx.append(prx_dbm)

    p_rx.append(p_rx[-1])
    df.insert(7, "Walfish Ikegami", p_rx)
    return df


if __name__ == "__main__":
    main()










