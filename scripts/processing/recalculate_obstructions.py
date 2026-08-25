from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = ROOT_DIR / "data" / "processed" / "line_profiles"
OUTPUT_DIR = ROOT_DIR / "data" / "processed" / "corrected_profiles"


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

    antena = 155.98
    cota_tx = 825.8
    soma_cot_tx = antena + cota_tx
    a_rx = 9.1
    obstruct = []

    for i in range(len(altitude) - 1):
        flag_obs = False
        if soma_cot_tx > altitude[i] + a_rx:
            tg_teta = (soma_cot_tx - altitude[i] - a_rx) / distance_m[i]
        elif soma_cot_tx < altitude[i] + a_rx:
            tg_teta = (altitude[i] + a_rx - soma_cot_tx) / distance_m[i]
        else:
            tg_teta = 0

        for j in range(i, len(altitude)):
            x = tg_teta * distance_m[j]
            if soma_cot_tx > altitude[j] + a_rx:
                y = x + altitude[j] + a_rx
            elif soma_cot_tx < altitude[j] + a_rx:
                y = soma_cot_tx + x
            else:
                y = altitude[j] - a_rx

            if altitude[j] >= y:
                flag_obs = True

        obstruct.append(1 if flag_obs else 0)

    obstruct.append(0)
    df.insert(5, column="obstrucao", value=obstruct, allow_duplicates=True)

    output_path = OUTPUT_DIR / caminho_arquivo.name
    df.to_csv(output_path, sep=";", index=False)


if __name__ == "__main__":
    main()










